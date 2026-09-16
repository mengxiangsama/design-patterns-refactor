package examples;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.zip.GZIPInputStream;

import static org.junit.jupiter.api.Assertions.*;

class RefactoringTest {
    @ParameterizedTest
    @CsvSource({"REGULAR,100.005,100.01", "VIP,100.05,90.05",
            "PARTNER,123.45,98.76", "VIP,0,0.00", "REGULAR,0.001,0.00"})
    void priceContracts(PricingCase.Tier tier, String amount, String expected) {
        BigDecimal input = new BigDecimal(amount);
        BigDecimal before = new PricingCase.Before().quote(tier, input);
        BigDecimal after = PricingCase.standard().quote(tier, input);
        assertEquals(new BigDecimal(expected), before);
        assertEquals(before, after);
    }

    @Test void priceInvalidInputsKeepContract() {
        PricingCase.Before before = new PricingCase.Before();
        PricingCase.After after = PricingCase.standard();
        assertThrows(IllegalArgumentException.class, () -> before.quote(null, BigDecimal.ONE));
        assertThrows(IllegalArgumentException.class, () -> after.quote(null, BigDecimal.ONE));
        for (BigDecimal input : Arrays.asList(null, new BigDecimal("-1"))) {
            assertThrows(IllegalArgumentException.class,
                    () -> before.quote(PricingCase.Tier.VIP, input));
            assertThrows(IllegalArgumentException.class,
                    () -> after.quote(PricingCase.Tier.VIP, input));
        }
    }

    @Test void registryRejectsAmbiguousOrIncompleteConfiguration() {
        assertThrows(IllegalArgumentException.class, () -> new PricingCase.After(Arrays.asList(
                new PricingCase.Regular(), new PricingCase.Vip(), new PricingCase.Partner(),
                new PricingCase.Vip())));
        assertThrows(IllegalArgumentException.class, () ->
                new PricingCase.After(Collections.singletonList(new PricingCase.Regular())));
        assertThrows(IllegalArgumentException.class, () -> new PricingCase.After(null));
    }

    @Test void shippingMapsUnitsAndCallsExactlyOncePerRequest() {
        AtomicInteger calls = new AtomicInteger();
        ShippingCase.VendorClient vendor = (id, grams) -> {
            calls.incrementAndGet();
            assertEquals("demo-order", id);
            assertEquals(1250, grams);
            return new ShippingCase.VendorReply(0, "TRACK-1");
        };
        assertEquals("TRACK-1", new ShippingCase.Before(vendor)
                .ship("demo-order", new BigDecimal("1.250")));
        assertEquals("TRACK-1", new ShippingCase.After(new ShippingCase.VendorAdapter(vendor))
                .ship("demo-order", new BigDecimal("1.250")));
        assertEquals(2, calls.get());
    }

    @Test void shippingPreservesVendorFailure() {
        for (ShippingCase.VendorReply reply : Arrays.asList(
                new ShippingCase.VendorReply(42, null),
                new ShippingCase.VendorReply(0, ""), null)) {
            AtomicInteger calls = new AtomicInteger();
            ShippingCase.VendorClient vendor = (id, grams) -> { calls.incrementAndGet(); return reply; };
            ShippingCase.ShipmentFailure before = assertThrows(ShippingCase.ShipmentFailure.class,
                    () -> new ShippingCase.Before(vendor).ship("id", BigDecimal.ONE));
            ShippingCase.ShipmentFailure after = assertThrows(ShippingCase.ShipmentFailure.class,
                    () -> new ShippingCase.VendorAdapter(vendor).ship("id", BigDecimal.ONE));
            assertEquals(before.getMessage(), after.getMessage());
            assertEquals(2, calls.get());
        }
    }

    @Test void shippingDoesNotReplayTransportFailures() {
        AtomicInteger calls = new AtomicInteger();
        RuntimeException timeout = new RuntimeException("timeout");
        ShippingCase.VendorClient vendor = (id, grams) -> { calls.incrementAndGet(); throw timeout; };
        assertSame(timeout, assertThrows(RuntimeException.class,
                () -> new ShippingCase.Before(vendor).ship("id", BigDecimal.ONE)));
        assertSame(timeout, assertThrows(RuntimeException.class,
                () -> new ShippingCase.After(new ShippingCase.VendorAdapter(vendor))
                        .ship("id", BigDecimal.ONE)));
        assertEquals(2, calls.get());
    }

    @Test void shippingRejectsLossyConversionBeforeSideEffects() {
        AtomicInteger calls = new AtomicInteger();
        ShippingCase.VendorClient vendor = (id, grams) -> { calls.incrementAndGet(); return null; };
        for (BigDecimal weight : Arrays.asList(new BigDecimal("0.0001"),
                new BigDecimal("2147483.648"))) {
            assertThrows(ArithmeticException.class,
                    () -> new ShippingCase.Before(vendor).ship("id", weight));
            assertThrows(ArithmeticException.class,
                    () -> new ShippingCase.VendorAdapter(vendor).ship("id", weight));
        }
        for (BigDecimal weight : Arrays.asList(null, BigDecimal.ZERO, new BigDecimal("-1"))) {
            assertThrows(IllegalArgumentException.class,
                    () -> new ShippingCase.Before(vendor).ship("id", weight));
            assertThrows(IllegalArgumentException.class,
                    () -> new ShippingCase.VendorAdapter(vendor).ship("id", weight));
        }
        assertEquals(0, calls.get());
    }

    @Test void serviceCanUseAnotherVendorWithoutSdkTypes() {
        ShippingCase.After service = new ShippingCase.After((id, kg) -> "OTHER-" + id);
        assertEquals("OTHER-demo", service.ship("demo", BigDecimal.ONE));
    }

    @Test void exporterPreservesAllLegacyCombinations() throws IOException {
        List<String> cells = Arrays.asList("中文", "a,b", "a\"b", "line\nbreak");
        byte[] expected = "\"中文\",\"a,b\",\"a\"\"b\",\"line\nbreak\"\r\n"
                .getBytes(StandardCharsets.UTF_8);
        assertArrayEquals(expected, new ExportCase.Csv().export(cells));
        for (boolean compressed : new boolean[]{false, true}) {
            for (boolean encoded : new boolean[]{false, true}) {
                ExportCase.Exporter after = new ExportCase.Csv();
                if (compressed) after = new ExportCase.Gzip(after);
                if (encoded) after = new ExportCase.Encoded(after);
                byte[] bytes = after.export(cells);
                assertArrayEquals(new ExportCase.Before().export(cells, compressed, encoded), bytes);
                if (encoded) bytes = Base64.getDecoder().decode(bytes);
                if (compressed) bytes = gunzip(bytes);
                assertArrayEquals(expected, bytes);
            }
        }
    }

    @Test void decorationOrderIsPartOfProtocol() throws IOException {
        List<String> input = Arrays.asList("a", "b");
        byte[] csv = new ExportCase.Csv().export(input);
        byte[] normal = ExportCase.compressedAndEncoded().export(input);
        byte[] reversed = new ExportCase.Gzip(new ExportCase.Encoded(new ExportCase.Csv()))
                .export(input);
        assertFalse(Arrays.equals(normal, reversed));
        assertArrayEquals(csv, gunzip(Base64.getDecoder().decode(normal)));
        assertArrayEquals(csv, Base64.getDecoder().decode(gunzip(reversed)));
    }

    @Test void exporterKeepsEmptyAndNullContract() throws IOException {
        assertArrayEquals("\r\n".getBytes(StandardCharsets.UTF_8),
                new ExportCase.Csv().export(Collections.emptyList()));
        assertThrows(IllegalArgumentException.class,
                () -> new ExportCase.Before().export(null, true, true));
        assertThrows(IllegalArgumentException.class,
                () -> ExportCase.compressedAndEncoded().export(null));
        assertThrows(IllegalArgumentException.class,
                () -> ExportCase.compressedAndEncoded().export(Collections.singletonList(null)));
    }

    private static byte[] gunzip(byte[] bytes) throws IOException {
        try (GZIPInputStream input = new GZIPInputStream(new ByteArrayInputStream(bytes));
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[256];
            int size;
            while ((size = input.read(buffer)) != -1) output.write(buffer, 0, size);
            return output.toByteArray();
        }
    }
}
