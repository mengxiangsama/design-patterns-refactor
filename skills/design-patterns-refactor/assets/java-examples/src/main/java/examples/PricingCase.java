package examples;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

// 场景：计价规则由不同团队独立维护，需要逐个扩展与测试。
public final class PricingCase {
    private PricingCase() {}
    public enum Tier { REGULAR, VIP, PARTNER }

    private static void validate(Tier tier, BigDecimal amount) {
        if (tier == null || amount == null || amount.signum() < 0) {
            throw new IllegalArgumentException("tier and non-negative amount required");
        }
    }

    public static final class Before {
        public BigDecimal quote(Tier tier, BigDecimal amount) {
            validate(tier, amount);
            BigDecimal rate;
            switch (tier) {
                case VIP: rate = new BigDecimal("0.90"); break;
                case PARTNER: rate = new BigDecimal("0.80"); break;
                default: rate = BigDecimal.ONE;
            }
            return amount.multiply(rate).setScale(2, RoundingMode.HALF_UP);
        }
    }

    public interface PricingRule {
        Tier tier();
        BigDecimal quote(BigDecimal amount);
    }

    public static final class Regular implements PricingRule {
        public Tier tier() { return Tier.REGULAR; }
        public BigDecimal quote(BigDecimal amount) { return amount; }
    }

    public static final class Vip implements PricingRule {
        public Tier tier() { return Tier.VIP; }
        public BigDecimal quote(BigDecimal amount) {
            return amount.multiply(new BigDecimal("0.90"));
        }
    }

    public static final class Partner implements PricingRule {
        public Tier tier() { return Tier.PARTNER; }
        public BigDecimal quote(BigDecimal amount) {
            return amount.multiply(new BigDecimal("0.80"));
        }
    }

    public static final class After {
        private final Map<Tier, PricingRule> rules;

        public After(Collection<? extends PricingRule> candidates) {
            if (candidates == null) throw new IllegalArgumentException("rules required");
            Map<Tier, PricingRule> registry = new EnumMap<>(Tier.class);
            for (PricingRule rule : candidates) {
                if (rule == null || rule.tier() == null) {
                    throw new IllegalArgumentException("rule and tier required");
                }
                if (registry.put(rule.tier(), rule) != null) {
                    throw new IllegalArgumentException("duplicate tier: " + rule.tier());
                }
            }
            if (registry.size() != Tier.values().length) {
                throw new IllegalArgumentException("all legacy tiers must be supported");
            }
            rules = Collections.unmodifiableMap(registry);
        }

        public BigDecimal quote(Tier tier, BigDecimal amount) {
            validate(tier, amount);
            // 货币舍入属于稳定契约，由入口统一完成。
            return rules.get(tier).quote(amount).setScale(2, RoundingMode.HALF_UP);
        }
    }

    public static After standard() {
        return new After(Arrays.asList(new Regular(), new Vip(), new Partner()));
    }
}
