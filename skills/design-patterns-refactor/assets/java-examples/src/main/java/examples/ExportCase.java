package examples;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.zip.GZIPOutputStream;

// 场景：同一个输出合同需要组合可选压缩和传输编码。
public final class ExportCase {
    private ExportCase() {}

    public interface Exporter {
        byte[] export(List<String> cells) throws IOException;
    }

    public static final class Csv implements Exporter {
        public byte[] export(List<String> cells) {
            if (cells == null) throw new IllegalArgumentException("cells required");
            StringBuilder out = new StringBuilder();
            for (int i = 0; i < cells.size(); i++) {
                String cell = cells.get(i);
                if (cell == null) throw new IllegalArgumentException("cell required");
                if (i > 0) out.append(',');
                out.append('"').append(cell.replace("\"", "\"\"")).append('"');
            }
            return out.append("\r\n").toString().getBytes(StandardCharsets.UTF_8);
        }
    }

    private static byte[] gzip(byte[] data) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (GZIPOutputStream stream = new GZIPOutputStream(bytes)) {
            stream.write(data);
        }
        return bytes.toByteArray();
    }

    public static final class Before {
        public byte[] export(List<String> cells, boolean compressed, boolean encoded)
                throws IOException {
            byte[] data = new Csv().export(cells);
            if (compressed) data = gzip(data);
            if (encoded) data = Base64.getEncoder().encode(data);
            return data;
        }
    }

    public static final class Gzip implements Exporter {
        private final Exporter delegate;
        public Gzip(Exporter delegate) {
            if (delegate == null) throw new IllegalArgumentException("delegate required");
            this.delegate = delegate;
        }
        public byte[] export(List<String> cells) throws IOException {
            return gzip(delegate.export(cells));
        }
    }

    public static final class Encoded implements Exporter {
        private final Exporter delegate;
        public Encoded(Exporter delegate) {
            if (delegate == null) throw new IllegalArgumentException("delegate required");
            this.delegate = delegate;
        }
        public byte[] export(List<String> cells) throws IOException {
            return Base64.getEncoder().encode(delegate.export(cells));
        }
    }

    // 按原协议：先压缩后编码。反过来也是合法组合，但输出协议不同。
    public static Exporter compressedAndEncoded() {
        return new Encoded(new Gzip(new Csv()));
    }
}
