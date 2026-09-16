package examples;

import java.math.BigDecimal;

// 模拟外部 SDK：不是本项目 API，不为接入它修改业务接口。
public final class ShippingCase {
    private ShippingCase() {}

    public interface VendorClient {
        VendorReply create(String orderId, int grams);
    }

    public static final class VendorReply {
        public final int code;
        public final String tracking;
        public VendorReply(int code, String tracking) {
            this.code = code;
            this.tracking = tracking;
        }
    }

    public static final class ShipmentFailure extends RuntimeException {
        public ShipmentFailure(String message) { super(message); }
    }

    // 业务契约使用千克；供应商支持克整数，禁止静默截断。
    private static int grams(String orderId, BigDecimal kilograms) {
        if (orderId == null || orderId.trim().isEmpty()
                || kilograms == null || kilograms.signum() <= 0) {
            throw new IllegalArgumentException("orderId and positive kilograms required");
        }
        return kilograms.movePointRight(3).intValueExact();
    }

    private static String tracking(VendorReply reply) {
        if (reply == null) throw new ShipmentFailure("vendor returned no response");
        if (reply.code != 0) throw new ShipmentFailure("vendor code: " + reply.code);
        if (reply.tracking == null || reply.tracking.trim().isEmpty()) {
            throw new ShipmentFailure("vendor returned no tracking number");
        }
        return reply.tracking;
    }

    public static final class Before {
        private final VendorClient vendor;
        public Before(VendorClient vendor) {
            if (vendor == null) throw new IllegalArgumentException("vendor required");
            this.vendor = vendor;
        }
        public String ship(String orderId, BigDecimal kilograms) {
            return tracking(vendor.create(orderId, grams(orderId, kilograms)));
        }
    }

    public interface ShippingPort {
        String ship(String orderId, BigDecimal kilograms);
    }

    public static final class VendorAdapter implements ShippingPort {
        private final VendorClient vendor;
        public VendorAdapter(VendorClient vendor) {
            if (vendor == null) throw new IllegalArgumentException("vendor required");
            this.vendor = vendor;
        }
        public String ship(String orderId, BigDecimal kilograms) {
            // 不重试有副作用的发货请求；保留供应商异常与调用次数。
            return tracking(vendor.create(orderId, grams(orderId, kilograms)));
        }
    }

    public static final class After {
        private final ShippingPort shipping;
        public After(ShippingPort shipping) {
            if (shipping == null) throw new IllegalArgumentException("shipping required");
            this.shipping = shipping;
        }
        public String ship(String orderId, BigDecimal kilograms) {
            return shipping.ship(orderId, kilograms);
        }
    }
}
