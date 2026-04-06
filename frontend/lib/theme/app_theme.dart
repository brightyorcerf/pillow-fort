import 'package:flutter/material.dart';


class AppColors {
  // Backgrounds
  static const cream = Color(0xFFF5F0E8);
  static const creamDark = Color(0xFFEDE8DC);

  // Sage greens
  static const sage = Color(0xFFB5C4A8);
  static const sageDark = Color(0xFFA0B490);
  static const sageCard = Color(0xFFB8C9AB);

  // Browns
  static const brownDark = Color(0xFF2C1F14);
  static const brownMedium = Color(0xFF4A3728);
  static const brownLight = Color(0xFF7A6355);
  static const brownBorder = Color(0xFF3D2B1F);

  // Hearts / alerts
  static const heartRed = Color(0xFFE85555);
  static const missedRed = Color(0xFFD45555);

  // Text
  static const textDark = Color(0xFF2C1F14);
  static const textMedium = Color(0xFF5A4535);
  static const textLight = Color(0xFF8A7565);
}

class AppTheme {
  static ThemeData get theme => ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.cream,
        fontFamily: 'DynaPuff',
        colorScheme: ColorScheme.light(
          primary: AppColors.brownDark,
          secondary: AppColors.sage,
          surface: AppColors.cream,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: AppColors.cream,
          selectedItemColor: AppColors.brownDark,
          unselectedItemColor: AppColors.brownLight,
          selectedLabelStyle: TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 11,
            fontWeight: FontWeight.w600,
          ),
          unselectedLabelStyle: TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 11,
          ),
          showSelectedLabels: true,
          showUnselectedLabels: true,
          type: BottomNavigationBarType.fixed,
          elevation: 0,
        ),
      );
}

// Reusable border style — the chunky hand-made feel
BoxDecoration cardDecoration({
  Color fill = AppColors.sageCard,
  double radius = 20,
  double borderWidth = 3.0,
}) {
  return BoxDecoration(
    color: fill,
    borderRadius: BorderRadius.circular(radius),
    border: Border.all(
      color: AppColors.brownBorder,
      width: borderWidth,
    ),
    boxShadow: [
      BoxShadow(
        color: AppColors.brownBorder.withOpacity(0.25),
        offset: const Offset(3, 4),
        blurRadius: 0,
      ),
    ],
  );
}

// ============================================================================
// Responsive spacing helper
// Usage: AppSpacing.hPad(context)  → horizontal page padding
//        AppSpacing.vTop(context)  → top section spacing
// ============================================================================

class AppSpacing {
  AppSpacing._();

  /// Horizontal page padding: 14 (SE) → 18 (Pro) → 22 (Pro Max)
  static double hPad(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    return w < 375 ? 14.0 : (w > 430 ? 22.0 : 18.0);
  }

  /// Vertical top spacing: 16 (SE) → 20 (Pro) → 24 (Pro Max)
  static double vTop(BuildContext context) {
    final h = MediaQuery.of(context).size.height;
    return h < 668 ? 16.0 : (h > 844 ? 24.0 : 20.0);
  }

  /// Scale a base size proportionally to the device width.
  /// [base] is calibrated for a 390px (iPhone 15 Pro) screen.
  static double scale(BuildContext context, double base) {
    final w = MediaQuery.of(context).size.width;
    return base * (w / 390.0);
  }
}

// ============================================================================
// Shared text styles — use these instead of ad-hoc TextStyle() constructors
// ============================================================================

class AppTextStyles {
  AppTextStyles._();

  static const h1 = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 28,
    fontWeight: FontWeight.w700,
    color: AppColors.textDark,
  );

  static const h2 = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 20,
    fontWeight: FontWeight.w700,
    color: AppColors.textDark,
    height: 1.55,
  );

  static const h3 = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 17,
    fontWeight: FontWeight.w700,
    color: AppColors.textDark,
    height: 1.6,
  );

  static const body = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 13,
    color: AppColors.textMedium,
    height: 1.7,
  );

  static const caption = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 11,
    color: AppColors.textLight,
  );

  static const label = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: AppColors.textMedium,
  );

  static const btn = TextStyle(
    fontFamily: 'DynaPuff',
    fontSize: 15,
    fontWeight: FontWeight.w700,
    color: AppColors.cream,
  );
}
