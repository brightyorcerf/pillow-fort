import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'focus_session_screen.dart';

class SanctuaryScreen extends StatefulWidget {
  const SanctuaryScreen({super.key});

  @override
  State<SanctuaryScreen> createState() => _SanctuaryScreenState();
}

class _SanctuaryScreenState extends State<SanctuaryScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnim;

  // TODO: connect to backend
  final int hearts = 3;
  final String todayStudied = '2.5 hours';

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.97, end: 1.03).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.cream,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 20),
              _buildHeader(),
              const SizedBox(height: 8),
              _buildSubtitle(),
              const Spacer(),
              _buildMascotArea(),
              const Spacer(),
              _buildFocusButton(),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Text(
          'Your Sanctuary',
          style: TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 26,
            fontWeight: FontWeight.w700,
            color: AppColors.textDark,
          ),
        ),
        Row(
          children: List.generate(
            hearts,
            (i) => const Padding(
              padding: EdgeInsets.only(left: 4),
              child: Text('❤️', style: TextStyle(fontSize: 22)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSubtitle() {
    return Text(
      'today studied: $todayStudied',
      style: const TextStyle(
        fontFamily: 'DynaPuff',
        fontSize: 13,
        color: AppColors.textLight,
      ),
    );
  }

  Widget _buildMascotArea() {
    return Center(
      child: ScaleTransition(
        scale: _pulseAnim,
        child: Container(
          width: 260,
          height: 260,
          decoration: BoxDecoration(
            color: AppColors.sageCard,
            shape: BoxShape.circle,
            border: Border.all(
              color: AppColors.brownBorder,
              width: 3.5,
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.brownBorder.withOpacity(0.2),
                offset: const Offset(4, 6),
                blurRadius: 0,
              ),
            ],
          ),
          child: Center(
            child: Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: AppColors.brownBorder.withOpacity(0.3),
                  width: 2,
                  style: BorderStyle.solid,
                ),
              ),
              // TODO: Replace with your Rive widget:
              // child: RiveAnimation.asset('assets/mascot.riv'),
              child: const Icon(
                Icons.pets_rounded,
                color: AppColors.brownLight,
                size: 28,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFocusButton() {
    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          PageRouteBuilder(
            pageBuilder: (_, anim, __) => const FocusSessionScreen(),
            transitionsBuilder: (_, anim, __, child) => FadeTransition(
              opacity: anim,
              child: SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(0, 0.08),
                  end: Offset.zero,
                ).animate(CurvedAnimation(parent: anim, curve: Curves.easeOut)),
                child: child,
              ),
            ),
          ),
        );
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 18),
        decoration: BoxDecoration(
          color: AppColors.brownDark,
          borderRadius: BorderRadius.circular(50),
          border: Border.all(color: AppColors.brownBorder, width: 2.5),
          boxShadow: [
            BoxShadow(
              color: AppColors.brownBorder.withOpacity(0.5),
              offset: const Offset(3, 5),
              blurRadius: 0,
            ),
          ],
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.timer_outlined, color: AppColors.cream, size: 22),
            SizedBox(width: 10),
            Text(
              'Focus NOW',
              style: TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 17,
                fontWeight: FontWeight.w700,
                color: AppColors.cream,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
