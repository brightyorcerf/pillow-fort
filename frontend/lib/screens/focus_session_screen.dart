import 'dart:async';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class FocusSessionScreen extends StatefulWidget {
  const FocusSessionScreen({super.key});

  @override
  State<FocusSessionScreen> createState() => _FocusSessionScreenState();
}

class _FocusSessionScreenState extends State<FocusSessionScreen>
    with SingleTickerProviderStateMixin {
  static const int _defaultMinutes = 25;
  int _totalSeconds = _defaultMinutes * 60;
  int _remainingSeconds = _defaultMinutes * 60;
  bool _isRunning = false;
  Timer? _timer;

  late AnimationController _cardAnim;
  late Animation<double> _cardScale;

  @override
  void initState() {
    super.initState();
    _cardAnim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    )..forward();
    _cardScale = CurvedAnimation(parent: _cardAnim, curve: Curves.easeOutBack);
  }

  @override
  void dispose() {
    _timer?.cancel();
    _cardAnim.dispose();
    super.dispose();
  }

  void _startTimer() {
    setState(() => _isRunning = true);
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_remainingSeconds <= 0) {
        t.cancel();
        setState(() => _isRunning = false);
        _onSessionComplete();
      } else {
        setState(() => _remainingSeconds--);
      }
    });
  }

  void _pauseTimer() {
    _timer?.cancel();
    setState(() => _isRunning = false);
  }

  void _resetTimer() {
    _timer?.cancel();
    setState(() {
      _isRunning = false;
      _remainingSeconds = _totalSeconds;
    });
  }

  void _onSessionComplete() {
    // TODO: notify backend of completed session
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppColors.cream,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: AppColors.brownBorder, width: 2.5),
        ),
        title: const Text(
          'Session Complete! 🎉',
          style: TextStyle(
            fontFamily: 'DynaPuff',
            color: AppColors.textDark,
            fontSize: 18,
          ),
        ),
        content: const Text(
          'Great work! Time for a break.',
          style: TextStyle(
            fontFamily: 'DynaPuff',
            color: AppColors.textMedium,
            fontSize: 14,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              setState(() => _remainingSeconds = _totalSeconds);
            },
            child: const Text(
              'Done',
              style: TextStyle(
                fontFamily: 'DynaPuff',
                color: AppColors.brownDark,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _editDuration() async {
    int? picked = await showModalBottomSheet<int>(
      context: context,
      backgroundColor: AppColors.cream,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        side: BorderSide(color: AppColors.brownBorder, width: 2),
      ),
      builder: (_) => _DurationPicker(currentMinutes: _totalSeconds ~/ 60),
    );
    if (picked != null) {
      setState(() {
        _totalSeconds = picked * 60;
        _remainingSeconds = _totalSeconds;
        _isRunning = false;
      });
      _timer?.cancel();
    }
  }

  String get _timeDisplay {
    final m = (_remainingSeconds ~/ 60).toString().padLeft(2, '0');
    final s = (_remainingSeconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  double get _progress => _remainingSeconds / _totalSeconds;

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
              _buildBackButton(),
              const SizedBox(height: 36),
              _buildSessionLabel(),
              const SizedBox(height: 24),
              _buildTimerCard(),
              const SizedBox(height: 36),
              _buildControls(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBackButton() {
    return GestureDetector(
      onTap: () => Navigator.of(context).pop(),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.arrow_back_ios_new_rounded,
              size: 16, color: AppColors.textDark),
          SizedBox(width: 6),
          Text(
            'Back',
            style: TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 15,
              color: AppColors.textDark,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionLabel() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Focus Session (${_totalSeconds ~/ 60} min)',
          style: const TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 15,
            color: AppColors.textMedium,
          ),
        ),
        const SizedBox(width: 10),
        GestureDetector(
          onTap: _editDuration,
          child: const Text(
            'Edit',
            style: TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 15,
              color: AppColors.brownDark,
              decoration: TextDecoration.underline,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTimerCard() {
    return ScaleTransition(
      scale: _cardScale,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 52),
        decoration: cardDecoration(radius: 28, borderWidth: 3.5),
        child: Column(
          children: [
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 1.0, end: _isRunning ? 1.06 : 1.0),
              duration: const Duration(milliseconds: 300),
              builder: (_, scale, child) => Transform.scale(
                scale: scale,
                child: child,
              ),
              child: Text(
                _timeDisplay,
                style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 72,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                  height: 1,
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Progress bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: _progress,
                  backgroundColor: AppColors.brownBorder.withOpacity(0.15),
                  valueColor: AlwaysStoppedAnimation<Color>(
                    AppColors.brownMedium.withOpacity(0.5),
                  ),
                  minHeight: 6,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControls() {
    return Row(
      children: [
        // Start / Pause
        Expanded(
          child: GestureDetector(
            onTap: _isRunning ? _pauseTimer : _startTimer,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 18),
              decoration: BoxDecoration(
                color: AppColors.sageCard,
                borderRadius: BorderRadius.circular(50),
                border: Border.all(color: AppColors.brownBorder, width: 2.5),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.brownBorder.withOpacity(0.3),
                    offset: const Offset(3, 4),
                    blurRadius: 0,
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  _isRunning ? 'Pause' : 'Start',
                  style: const TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textDark,
                  ),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        // Reset button
        GestureDetector(
          onTap: _resetTimer,
          child: Container(
            width: 70,
            height: 58,
            decoration: BoxDecoration(
              color: AppColors.brownDark,
              borderRadius: BorderRadius.circular(50),
              border: Border.all(color: AppColors.brownBorder, width: 2.5),
              boxShadow: [
                BoxShadow(
                  color: AppColors.brownBorder.withOpacity(0.4),
                  offset: const Offset(3, 4),
                  blurRadius: 0,
                ),
              ],
            ),
            child: const Icon(
              Icons.refresh_rounded,
              color: AppColors.cream,
              size: 26,
            ),
          ),
        ),
      ],
    );
  }
}

class _DurationPicker extends StatefulWidget {
  final int currentMinutes;
  const _DurationPicker({required this.currentMinutes});

  @override
  State<_DurationPicker> createState() => _DurationPickerState();
}

class _DurationPickerState extends State<_DurationPicker> {
  late int _selected;
  final List<int> _options = [5, 10, 15, 20, 25, 30, 45, 60, 90];

  @override
  void initState() {
    super.initState();
    _selected = widget.currentMinutes;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Session Duration',
            style: TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: AppColors.textDark,
            ),
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: _options.map((min) {
              final selected = min == _selected;
              return GestureDetector(
                onTap: () => setState(() => _selected = min),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                  decoration: BoxDecoration(
                    color:
                        selected ? AppColors.brownDark : AppColors.sageCard,
                    borderRadius: BorderRadius.circular(50),
                    border: Border.all(
                        color: AppColors.brownBorder, width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.brownBorder.withOpacity(0.2),
                        offset: const Offset(2, 3),
                        blurRadius: 0,
                      ),
                    ],
                  ),
                  child: Text(
                    '$min min',
                    style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 14,
                      color: selected ? AppColors.cream : AppColors.textDark,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: GestureDetector(
              onTap: () => Navigator.of(context).pop(_selected),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 16),
                decoration: BoxDecoration(
                  color: AppColors.brownDark,
                  borderRadius: BorderRadius.circular(50),
                  border:
                      Border.all(color: AppColors.brownBorder, width: 2.5),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.brownBorder.withOpacity(0.4),
                      offset: const Offset(3, 4),
                      blurRadius: 0,
                    ),
                  ],
                ),
                child: const Center(
                  child: Text(
                    'Confirm',
                    style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 16,
                      color: AppColors.cream,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
