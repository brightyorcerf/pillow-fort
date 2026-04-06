import 'package:flutter/material.dart';
import '../models/shop_item.dart';
import '../theme/app_theme.dart';
import '../widgets/shop_card.dart';

// ---------------------------------------------------------------------------
// shop_screen.dart (Refactored)
//
// To add a new shop item:
//   1. Open lib/models/shop_item.dart
//   2. Add a new ShopItem entry to the [shopItems] list
//   3. (Optional) Drop assets/items/<id>.png into the assets folder
//   → That's it. No UI code needed.
// ---------------------------------------------------------------------------

class ShopScreen extends StatefulWidget {
  const ShopScreen({super.key});

  @override
  State<ShopScreen> createState() => _ShopScreenState();
}

class _ShopScreenState extends State<ShopScreen> {
  String _activeCategory = 'Snacks';
  final List<String> _categories = ['Snacks', 'Decor', 'Special'];

  // TODO: Replace with a real star count from your state management / backend
  final int _stars = 480;

  List<ShopItem> get _filtered =>
      shopItems.where((i) => i.category == _activeCategory).toList();

  void _openItemDetail(ShopItem item) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: 'Close',
      barrierColor: AppColors.brownDark.withOpacity(0.45),
      transitionDuration: const Duration(milliseconds: 300),
      pageBuilder: (_, __, ___) => const SizedBox.shrink(),
      transitionBuilder: (ctx, anim, __, ___) {
        final curved =
            CurvedAnimation(parent: anim, curve: Curves.easeOutBack);
        return ScaleTransition(
          scale: curved,
          child: FadeTransition(
            opacity: anim,
            child: _ItemDetailDialog(item: item, stars: _stars),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final mq = MediaQuery.of(context);
    final screenW = mq.size.width;
    // Responsive horizontal padding: tighter on SE, more generous on Pro Max
    final hPad = screenW < 375 ? 14.0 : (screenW > 430 ? 22.0 : 18.0);

    return Scaffold(
      backgroundColor: AppColors.cream,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(child: _buildTopSection(hPad, screenW)),
            SliverToBoxAdapter(child: _buildDailySpecial(hPad)),
            SliverToBoxAdapter(child: _buildCategoryTabs(hPad)),
            SliverPadding(
              padding: EdgeInsets.symmetric(horizontal: hPad),
              sliver: SliverGrid(
                delegate: SliverChildBuilderDelegate(
                  (_, i) => ShopCard(
                    item: _filtered[i],
                    onTap: () => _openItemDetail(_filtered[i]),
                  ),
                  childCount: _filtered.length,
                ),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 14,
                  mainAxisSpacing: 14,
                  childAspectRatio: 0.78,
                ),
              ),
            ),
            SliverToBoxAdapter(child: _buildFooter(hPad)),
          ],
        ),
      ),
    );
  }

  Widget _buildTopSection(double hPad, double screenW) {
    // Banner height scales with screen width
    final bannerH = screenW < 375 ? 90.0 : (screenW > 430 ? 130.0 : 110.0);

    return Padding(
      padding: EdgeInsets.fromLTRB(hPad, 20, hPad, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            height: bannerH,
            decoration: BoxDecoration(
              color: AppColors.creamDark,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: AppColors.brownBorder.withOpacity(0.35),
                width: 2.5,
              ),
            ),
            child: CustomPaint(
              painter: _DashedBorderPainter(),
              child: const Center(
                child: Text(
                  'Banner Space',
                  style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 13,
                    color: AppColors.textLight,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'SHOP',
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                ),
              ),
              _StarBalance(stars: _stars),
            ],
          ),
          const SizedBox(height: 14),
        ],
      ),
    );
  }

  Widget _buildDailySpecial(double hPad) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: hPad),
      child: GestureDetector(
        onTap: () => _openItemDetail(dailySpecialItem),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFFFFF0C2),
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: const Color(0xFFBF8A30), width: 3),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFFBF8A30).withOpacity(0.3),
                offset: const Offset(3, 4),
                blurRadius: 0,
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 62,
                height: 62,
                decoration: BoxDecoration(
                  color: AppColors.cream,
                  shape: BoxShape.circle,
                  border:
                      Border.all(color: const Color(0xFFBF8A30), width: 2.5),
                ),
                child: ClipOval(
                  child: Image.asset(
                    dailySpecialItem.resolvedImagePath,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => const Center(
                      child: Text('🫖', style: TextStyle(fontSize: 28)),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Text('🕐 ', style: TextStyle(fontSize: 13)),
                        Text(
                          'Daily Special',
                          style: TextStyle(
                            fontFamily: 'DynaPuff',
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFFBF8A30),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 3),
                    const Text(
                      "Koko's Secret Blend",
                      style: TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textDark,
                      ),
                    ),
                    const SizedBox(height: 2),
                    const Text(
                      'Only available today. Boosts XP ✨',
                      style: TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 10,
                        color: AppColors.textMedium,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const ShopRarityDots(rarity: ItemRarity.legendary),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Column(
                children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFFBF8A30),
                      borderRadius: BorderRadius.circular(50),
                      border: Border.all(
                          color: AppColors.brownBorder, width: 1.5),
                    ),
                    child: const Text(
                      'TODAY ONLY',
                      style: TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 8,
                        fontWeight: FontWeight.w700,
                        color: AppColors.cream,
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  const ShopPricePill(price: 200),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCategoryTabs(double hPad) {
    return Padding(
      padding: EdgeInsets.fromLTRB(hPad, 18, hPad, 14),
      child: Row(
        children: _categories.map((cat) {
          final isActive = _activeCategory == cat;
          final emoji =
              cat == 'Snacks' ? '🍡' : cat == 'Decor' ? '🪴' : '✨';
          return Padding(
            padding: const EdgeInsets.only(right: 10),
            child: GestureDetector(
              onTap: () => setState(() => _activeCategory = cat),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 9),
                decoration: BoxDecoration(
                  color: isActive ? AppColors.brownDark : AppColors.cream,
                  borderRadius: BorderRadius.circular(50),
                  border: Border.all(
                    color: AppColors.brownBorder,
                    width: isActive ? 2.5 : 2,
                  ),
                  boxShadow: isActive
                      ? [
                          BoxShadow(
                            color: AppColors.brownBorder.withOpacity(0.35),
                            offset: const Offset(2, 3),
                            blurRadius: 0,
                          ),
                        ]
                      : null,
                ),
                child: Text(
                  '$emoji $cat',
                  style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isActive ? AppColors.cream : AppColors.textMedium,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildFooter(double hPad) {
    return Padding(
      padding: EdgeInsets.fromLTRB(hPad, 20, hPad, 24),
      child: Container(
        width: double.infinity,
        padding:
            const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
        decoration: BoxDecoration(
          color: AppColors.creamDark,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: AppColors.brownBorder.withOpacity(0.25),
            width: 2,
          ),
        ),
        child: const Text(
          'whenever the dev isn\'t feeling lazy\nkeep focusing to earn more ⭐',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 12,
            color: AppColors.textLight,
            height: 1.6,
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Star balance pill
// ---------------------------------------------------------------------------

class _StarBalance extends StatelessWidget {
  final int stars;
  const _StarBalance({required this.stars});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
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
          const Text('⭐', style: TextStyle(fontSize: 14)),
          const SizedBox(width: 5),
          Text(
            '$stars',
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

// ---------------------------------------------------------------------------
// Item detail dialog
// ---------------------------------------------------------------------------

class _ItemDetailDialog extends StatefulWidget {
  final ShopItem item;
  final int stars;
  const _ItemDetailDialog({required this.item, required this.stars});

  @override
  State<_ItemDetailDialog> createState() => _ItemDetailDialogState();
}

class _ItemDetailDialogState extends State<_ItemDetailDialog> {
  bool _purchased = false;

  bool get _canAfford => widget.stars >= widget.item.price;

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final mq = MediaQuery.of(context);
    final dialogW = mq.size.width * 0.82;

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: EdgeInsets.zero,
      child: Center(
        child: Container(
          width: dialogW,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: cardBgColor(item),
            borderRadius: BorderRadius.circular(28),
            border: Border.all(color: AppColors.brownBorder, width: 3.5),
            boxShadow: [
              BoxShadow(
                color: AppColors.brownBorder.withOpacity(0.35),
                offset: const Offset(5, 7),
                blurRadius: 0,
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Align(
                alignment: Alignment.topRight,
                child: GestureDetector(
                  onTap: () => Navigator.of(context).pop(),
                  child: Container(
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: AppColors.brownDark,
                      shape: BoxShape.circle,
                      border: Border.all(
                          color: AppColors.brownBorder, width: 2),
                    ),
                    child: const Icon(Icons.close_rounded,
                        color: AppColors.cream, size: 16),
                  ),
                ),
              ),
              const SizedBox(height: 6),
              // Large item image
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: AppColors.cream,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.brownBorder, width: 3),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.brownBorder.withOpacity(0.2),
                      offset: const Offset(3, 4),
                      blurRadius: 0,
                    ),
                  ],
                ),
                child: ClipOval(
                  child: Image.asset(
                    item.resolvedImagePath,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Center(
                      child: Text(
                        _emojiFallback(item.id),
                        style: const TextStyle(fontSize: 48),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 14),
              Text(
                item.name,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                item.description,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 11,
                  color: AppColors.textMedium,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 10),
              ShopRarityDots(rarity: item.rarity),
              const SizedBox(height: 20),
              // Buy button
              GestureDetector(
                onTap: _purchased || !_canAfford
                    ? null
                    : () => setState(() => _purchased = true),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 250),
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  decoration: BoxDecoration(
                    color: _purchased
                        ? AppColors.sageDark
                        : _canAfford
                            ? AppColors.brownDark
                            : AppColors.brownLight,
                    borderRadius: BorderRadius.circular(50),
                    border: Border.all(
                        color: AppColors.brownBorder, width: 2.5),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.brownBorder.withOpacity(0.4),
                        offset: const Offset(3, 4),
                        blurRadius: 0,
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (_purchased) ...[
                        const Icon(Icons.check_circle_rounded,
                            color: AppColors.cream, size: 18),
                        const SizedBox(width: 8),
                        const Text(
                          'Added to Bag!',
                          style: TextStyle(
                            fontFamily: 'DynaPuff',
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: AppColors.cream,
                          ),
                        ),
                      ] else ...[
                        const Text('⭐', style: TextStyle(fontSize: 15)),
                        const SizedBox(width: 6),
                        Text(
                          _canAfford
                              ? 'Buy for ${item.price}'
                              : 'Not enough ⭐',
                          style: const TextStyle(
                            fontFamily: 'DynaPuff',
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: AppColors.cream,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _emojiFallback(String id) {
    const map = {
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
    return map[id] ?? '🎁';
  }
}

// ---------------------------------------------------------------------------
// Dashed border painter (banner placeholder)
// ---------------------------------------------------------------------------

class _DashedBorderPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.brownBorder.withOpacity(0.4)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    const dashWidth = 8.0;
    const dashSpace = 5.0;
    const radius = Radius.circular(20);
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final rrect = RRect.fromRectAndRadius(rect, radius);
    final path = Path()..addRRect(rrect);
    final metrics = path.computeMetrics();

    for (final metric in metrics) {
      double distance = 0;
      bool draw = true;
      while (distance < metric.length) {
        final len = draw ? dashWidth : dashSpace;
        if (draw) {
          canvas.drawPath(
            metric.extractPath(distance, distance + len),
            paint,
          );
        }
        distance += len;
        draw = !draw;
      }
    }
  }

  @override
  bool shouldRepaint(_DashedBorderPainter old) => false;
}
