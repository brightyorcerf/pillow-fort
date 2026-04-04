import 'package:flutter/material.dart';
import '../models/shop_item.dart';
import '../theme/app_theme.dart';

// ---------------------------------------------------------------------------
// widgets/shop_card.dart
//
// Reusable grid tile for the Cosy Shop.
//
// Usage:
//   ShopCard(item: myItem, onTap: () => _openDetail(myItem))
//
// Image loading:
//   - Tries to load from: assets/items/<item.id>.png
//   - If the PNG doesn't exist, falls back gracefully to the emoji widget.
//   - Add new items by adding to shopItems in models/shop_item.dart and
//     dropping <id>.png into assets/items/. No UI code changes needed.
// ---------------------------------------------------------------------------

// ── Rarity helpers (package-private) ────────────────────────────────────────

Color rarityColor(ItemRarity r) {
  switch (r) {
    case ItemRarity.common:
      return AppColors.brownLight;
    case ItemRarity.rare:
      return const Color(0xFF5B7FCE);
    case ItemRarity.legendary:
      return const Color(0xFFBF8A30);
  }
}

String rarityLabel(ItemRarity r) {
  switch (r) {
    case ItemRarity.common:
      return 'Common';
    case ItemRarity.rare:
      return 'Rare';
    case ItemRarity.legendary:
      return 'Legendary';
  }
}

int rarityDots(ItemRarity r) {
  switch (r) {
    case ItemRarity.common:
      return 1;
    case ItemRarity.rare:
      return 2;
    case ItemRarity.legendary:
      return 3;
  }
}

Color cardBgColor(ShopItem item) {
  switch (item.rarity) {
    case ItemRarity.legendary:
      return const Color(0xFFFFF3D4);
    case ItemRarity.rare:
      return const Color(0xFFECE8F8);
    default:
      break;
  }
  if (item.isNew) return const Color(0xFFE8F4E8);
  return const Color(0xFFFFF8EE);
}

// ── Main public widget ───────────────────────────────────────────────────────

class ShopCard extends StatefulWidget {
  final ShopItem item;
  final VoidCallback onTap;

  const ShopCard({super.key, required this.item, required this.onTap});

  @override
  State<ShopCard> createState() => _ShopCardState();
}

class _ShopCardState extends State<ShopCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pressCtrl;
  late final Animation<double> _pressSc;

  @override
  void initState() {
    super.initState();
    _pressCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
      reverseDuration: const Duration(milliseconds: 180),
    );
    _pressSc = Tween(begin: 1.0, end: 0.95)
        .animate(CurvedAnimation(parent: _pressCtrl, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _pressCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    return GestureDetector(
      onTapDown: (_) => _pressCtrl.forward(),
      onTapUp: (_) {
        _pressCtrl.reverse();
        widget.onTap();
      },
      onTapCancel: () => _pressCtrl.reverse(),
      child: ScaleTransition(
        scale: _pressSc,
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: cardBgColor(item),
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: AppColors.brownBorder, width: 3),
            boxShadow: [
              BoxShadow(
                color: AppColors.brownBorder.withOpacity(0.25),
                offset: const Offset(3, 4),
                blurRadius: 0,
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              _ItemBadge(item: item),
              const SizedBox(height: 6),
              _ItemImage(item: item),
              const SizedBox(height: 10),
              Text(
                item.name,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                item.description,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 9,
                  color: AppColors.textMedium,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 6),
              ShopRarityDots(rarity: item.rarity),
              const Spacer(),
              ShopPricePill(price: item.price),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Item image: tries PNG asset, falls back to emoji ────────────────────────

class _ItemImage extends StatelessWidget {
  final ShopItem item;
  // Emoji fallback map — keeps the old emoji display working
  static const _emojiMap = {
    'matcha_mochi_ball': '🍡',
    'honey_cloud_cookie': '🍪',
    'cherry_blossom_tea': '🍵',
    'berry_focus_smoothie': '🥤',
    'moon_rice_crackers': '🍙',
    'golden_honey_cake': '🍰',
    'tiny_bonsai_pot': '🪴',
    'cinnamon_candle': '🕯️',
    'moon_lamp': '🌙',
    'star_night_poster': '⭐',
    'focus_ribbon_badge': '🎀',
    'sparkle_aura_pack': '✨',
    'kokos_secret_blend': '🫖',
  };

  const _ItemImage({required this.item});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 72,
      height: 72,
      decoration: BoxDecoration(
        color: AppColors.cream,
        shape: BoxShape.circle,
        border: Border.all(color: AppColors.brownBorder, width: 2.5),
      ),
      child: ClipOval(
        child: Image.asset(
          item.resolvedImagePath,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => Center(
            child: Text(
              _emojiMap[item.id] ?? '🎁',
              style: const TextStyle(fontSize: 34),
            ),
          ),
        ),
      ),
    );
  }
}

// ── Badge (NEW / LIMITED) ────────────────────────────────────────────────────

class _ItemBadge extends StatelessWidget {
  final ShopItem item;
  const _ItemBadge({required this.item});

  @override
  Widget build(BuildContext context) {
    if (item.isLimited) {
      return _badge('LIMITED', const Color(0xFFBF8A30));
    }
    if (item.isNew) {
      return _badge('NEW', AppColors.sageDark);
    }
    return const SizedBox(height: 18);
  }

  Widget _badge(String text, Color color) => Align(
        alignment: Alignment.topLeft,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(50),
            border: Border.all(color: AppColors.brownBorder, width: 1.5),
          ),
          child: Text(
            text,
            style: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 8,
              fontWeight: FontWeight.w700,
              color: AppColors.cream,
            ),
          ),
        ),
      );
}

// ── Rarity dots (exported for reuse in detail dialog) ───────────────────────

class ShopRarityDots extends StatelessWidget {
  final ItemRarity rarity;
  const ShopRarityDots({super.key, required this.rarity});

  @override
  Widget build(BuildContext context) {
    final color = rarityColor(rarity);
    final count = rarityDots(rarity);
    final label = rarityLabel(rarity);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ...List.generate(3, (i) {
          return Padding(
            padding: const EdgeInsets.only(right: 3),
            child: Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: i < count ? color : color.withOpacity(0.2),
                shape: BoxShape.circle,
                border: Border.all(color: color.withOpacity(0.5), width: 1),
              ),
            ),
          );
        }),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 9,
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

// ── Price pill (exported for reuse in detail dialog) ─────────────────────────

class ShopPricePill extends StatelessWidget {
  final int price;
  const ShopPricePill({super.key, required this.price});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.brownDark,
        borderRadius: BorderRadius.circular(50),
        border: Border.all(color: AppColors.brownBorder, width: 2),
        boxShadow: [
          BoxShadow(
            color: AppColors.brownBorder.withOpacity(0.4),
            offset: const Offset(2, 3),
            blurRadius: 0,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('⭐', style: TextStyle(fontSize: 13)),
          const SizedBox(width: 5),
          Text(
            '$price',
            style: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: AppColors.cream,
            ),
          ),
        ],
      ),
    );
  }
}
