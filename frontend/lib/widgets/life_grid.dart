import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// 80-year life grid. Filled cells = [age] years lived. Outline = remaining.
class LifeGridWidget extends StatelessWidget {
  final int age;
  const LifeGridWidget({super.key, required this.age});

  static const _total = 80;
  static const _livedColor = Color(0xFF8C7B6B);
  static const _livedBorder = Color(0xFF6B5A4E);

  @override
  Widget build(BuildContext context) {
    final lived = age.clamp(0, _total);
    final remaining = _total - lived;
    final pct = lived / _total * 100;

    return Column(crossAxisAlignment: CrossAxisAlignment.center, children: [
      // Big % number
      RichText(
        text: TextSpan(children: [
          TextSpan(
            text: pct.toStringAsFixed(1),
            style: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 46,
              fontWeight: FontWeight.w700,
              color: AppColors.textDark,
            ),
          ),
          const TextSpan(
            text: '%',
            style: TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 26,
              fontWeight: FontWeight.w700,
              color: AppColors.textDark,
            ),
          ),
        ]),
      ),
      const SizedBox(height: 4),
      const Text(
        'of our 80 years is already written in memory.',
        textAlign: TextAlign.center,
        style: TextStyle(
            fontFamily: 'DynaPuff', fontSize: 12, color: AppColors.textMedium),
      ),
      const SizedBox(height: 16),

      // Grid — 10 cols × 8 rows = 80 cells
      GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 10,
          crossAxisSpacing: 4,
          mainAxisSpacing: 4,
          childAspectRatio: 1,
        ),
        itemCount: _total,
        itemBuilder: (_, i) {
          final isLived = i < lived;
          return Container(
            decoration: BoxDecoration(
              color: isLived ? _livedColor : Colors.transparent,
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: isLived
                    ? _livedBorder
                    : AppColors.sageDark.withOpacity(0.45),
                width: 1.5,
              ),
            ),
          );
        },
      ),
      const SizedBox(height: 10),

      // Legend row
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Row(children: [
          Container(
            width: 11,
            height: 11,
            decoration: BoxDecoration(
              color: _livedColor,
              borderRadius: BorderRadius.circular(3),
              border: Border.all(color: _livedBorder, width: 1.5),
            ),
          ),
          const SizedBox(width: 6),
          Text(
            '■ Memory ($lived yrs)',
            style: const TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 10,
                color: AppColors.textMedium),
          ),
        ]),
        Row(children: [
          Text(
            '□ Remaining ($remaining yrs)',
            style: TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 10,
                color: AppColors.sageDark),
          ),
          const SizedBox(width: 6),
          Container(
            width: 11,
            height: 11,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(3),
              border: Border.all(
                  color: AppColors.sageDark.withOpacity(0.45), width: 1.5),
            ),
          ),
        ]),
      ]),
    ]);
  }
}
