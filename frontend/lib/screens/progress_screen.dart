import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

// ---------------------------------------------------------------------------
// Mock data — replace with backend calls
// ---------------------------------------------------------------------------
const List<double> _weekData = [1.0, 2.5, 2.0, 4.5, 3.5, 5.0, 4.0];
const List<String> _weekLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

// null = missed, 0+ = hours studied
final List<double?> _thirtyDayData = List.generate(30, (i) {
  if (i < 3 || i == 7 || i == 14 || i == 20 || i == 25) return null; // missed
  return (math.Random(i * 13).nextDouble() * 4 + 0.5);
});

class ProgressScreen extends StatefulWidget {
  const ProgressScreen({super.key});

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _chartAnim;
  late Animation<double> _chartProgress;

  // TODO: pull from backend
  final double totalHours = 47.5;
  final int dayStreak = 12;
  final int sessions = 23;
  final int focusRate = 94;

  @override
  void initState() {
    super.initState();
    _chartAnim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );
    _chartProgress = CurvedAnimation(
      parent: _chartAnim,
      curve: Curves.easeInOut,
    );
    // Start drawing after brief delay
    Future.delayed(const Duration(milliseconds: 250), () {
      if (mounted) _chartAnim.forward();
    });
  }

  @override
  void dispose() {
    _chartAnim.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.cream,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              const Text(
                'Your Progress',
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 26,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Keep up the great work!',
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 13,
                  color: AppColors.textLight,
                ),
              ),
              const SizedBox(height: 24),
              _buildStatsGrid(),
              const SizedBox(height: 20),
              _buildChartCard(),
              const SizedBox(height: 20),
              _buildActivityCard(),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatsGrid() {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 14,
      mainAxisSpacing: 14,
      childAspectRatio: 1.4,
      children: [
        _StatCard(value: '$totalHours', label: 'Total Hours'),
        _StatCard(value: '$dayStreak', label: 'Day Streak'),
        _StatCard(value: '$sessions', label: 'Sessions'),
        _StatCard(value: '$focusRate%', label: 'Focus Rate'),
      ],
    );
  }

  Widget _buildChartCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: cardDecoration(radius: 24, borderWidth: 3),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "This Week's Focus",
            style: TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: AppColors.textDark,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 160,
            child: AnimatedBuilder(
              animation: _chartProgress,
              builder: (_, __) => CustomPaint(
                painter: _LineChartPainter(
                  data: _weekData,
                  labels: _weekLabels,
                  progress: _chartProgress.value,
                ),
                size: Size.infinite,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActivityCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: cardDecoration(radius: 24, borderWidth: 3),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '30-Day Activity',
            style: TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: AppColors.textDark,
            ),
          ),
          const SizedBox(height: 16),
          _buildActivityGrid(),
        ],
      ),
    );
  }

  Widget _buildActivityGrid() {
    // Show days of month, starting from day 1
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 7,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: 1,
      ),
      itemCount: 30,
      itemBuilder: (_, i) {
        final dayNum = i + 1;
        final hours = _thirtyDayData[i];
        final isMissed = hours == null;

        return _ActivityCell(
          day: dayNum,
          hours: hours,
          isMissed: isMissed,
        );
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Stat card
// ---------------------------------------------------------------------------
class _StatCard extends StatelessWidget {
  final String value;
  final String label;
  const _StatCard({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: cardDecoration(radius: 20, borderWidth: 3),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            value,
            style: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 32,
              fontWeight: FontWeight.w700,
              color: AppColors.textDark,
              height: 1,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            label,
            style: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 11,
              color: AppColors.textMedium,
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Activity grid cell
// ---------------------------------------------------------------------------
class _ActivityCell extends StatelessWidget {
  final int day;
  final double? hours;
  final bool isMissed;

  const _ActivityCell({
    required this.day,
    required this.hours,
    required this.isMissed,
  });

  @override
  Widget build(BuildContext context) {
    // Future days (beyond today): show greyed-out
    final today = DateTime.now().day;
    final isFuture = day > today;

    Color bg;
    Color border;
    Color textColor;
    String label;

    if (isFuture) {
      bg = AppColors.brownBorder.withOpacity(0.07);
      border = AppColors.brownBorder.withOpacity(0.15);
      textColor = AppColors.textLight.withOpacity(0.4);
      label = '$day';
    } else if (isMissed) {
      bg = AppColors.missedRed.withOpacity(0.18);
      border = AppColors.missedRed.withOpacity(0.5);
      textColor = AppColors.missedRed;
      label = '$day';
    } else {
      // Studied — intensity based on hours
      final intensity = ((hours ?? 0) / 6).clamp(0.3, 1.0);
      bg = AppColors.sageDark.withOpacity(intensity * 0.6 + 0.2);
      border = AppColors.brownBorder.withOpacity(0.4);
      textColor = AppColors.textDark;
      label = hours! < 10 ? hours!.toStringAsFixed(1) : '${hours!.round()}';
    }

    return Container(
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: border, width: 1.5),
      ),
      child: Center(
        child: Text(
          label,
          style: TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: isMissed || isFuture ? 10 : 9,
            fontWeight: FontWeight.w700,
            color: textColor,
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Animated line chart painter
// ---------------------------------------------------------------------------
class _LineChartPainter extends CustomPainter {
  final List<double> data;
  final List<String> labels;
  final double progress; // 0→1, animates the draw

  _LineChartPainter({
    required this.data,
    required this.labels,
    required this.progress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    const double leftPad = 28;
    const double bottomPad = 28;
    const double topPad = 10;
    final chartW = size.width - leftPad;
    final chartH = size.height - bottomPad - topPad;

    final maxVal = data.reduce(math.max);
    final minVal = 0.0;
    final range = maxVal - minVal;

    // Grid lines + Y labels
    final gridPaint = Paint()
      ..color = AppColors.brownBorder.withOpacity(0.12)
      ..strokeWidth = 1;
    final labelStyle = TextStyle(
      fontFamily: 'DynaPuff',
      fontSize: 9,
      color: AppColors.textLight.withOpacity(0.7),
    );

    for (int i = 0; i <= 3; i++) {
      final y = topPad + chartH - (i / 3) * chartH;
      canvas.drawLine(Offset(leftPad, y), Offset(size.width, y), gridPaint);
      final val = ((i / 3) * range).toStringAsFixed(0);
      _drawText(canvas, val, Offset(0, y - 6), labelStyle, leftPad - 4);
    }

    // X labels
    for (int i = 0; i < data.length; i++) {
      final x = leftPad + (i / (data.length - 1)) * chartW;
      _drawText(
        canvas,
        labels[i],
        Offset(x - 12, size.height - bottomPad + 6),
        labelStyle,
        30,
      );
    }

    // Build full path
    final points = <Offset>[];
    for (int i = 0; i < data.length; i++) {
      final x = leftPad + (i / (data.length - 1)) * chartW;
      final y = topPad + chartH - ((data[i] - minVal) / range) * chartH;
      points.add(Offset(x, y));
    }

    // Clip to animated progress
    final totalLen = _pathLength(points);
    final drawLen = totalLen * progress;

    // Draw line with dash-like progress clipping
    final linePaint = Paint()
      ..color = AppColors.brownDark
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..style = PaintingStyle.stroke;

    final path = Path();
    double accumulated = 0;
    bool started = false;

    for (int i = 0; i < points.length - 1; i++) {
      final segLen = (points[i + 1] - points[i]).distance;
      if (!started) {
        path.moveTo(points[i].dx, points[i].dy);
        started = true;
      }
      if (accumulated + segLen <= drawLen) {
        path.lineTo(points[i + 1].dx, points[i + 1].dy);
        accumulated += segLen;
      } else {
        final t = (drawLen - accumulated) / segLen;
        final px = points[i].dx + (points[i + 1].dx - points[i].dx) * t;
        final py = points[i].dy + (points[i + 1].dy - points[i].dy) * t;
        path.lineTo(px, py);
        break;
      }
    }

    canvas.drawPath(path, linePaint);

    // Draw dots up to progress
    final dotPaint = Paint()
      ..color = AppColors.brownDark
      ..style = PaintingStyle.fill;
    final dotBg = Paint()
      ..color = AppColors.sageCard
      ..style = PaintingStyle.fill;

    for (int i = 0; i < points.length; i++) {
      final pct = i / (points.length - 1);
      if (pct <= progress) {
        canvas.drawCircle(points[i], 6, dotBg);
        canvas.drawCircle(points[i], 6,
            Paint()
              ..color = AppColors.brownBorder
              ..style = PaintingStyle.stroke
              ..strokeWidth = 2);
        canvas.drawCircle(points[i], 3, dotPaint);
      }
    }
  }

  double _pathLength(List<Offset> pts) {
    double len = 0;
    for (int i = 0; i < pts.length - 1; i++) {
      len += (pts[i + 1] - pts[i]).distance;
    }
    return len;
  }

  void _drawText(Canvas c, String text, Offset offset, TextStyle style, double maxW) {
    final tp = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: maxW);
    tp.paint(c, offset);
  }

  @override
  bool shouldRepaint(_LineChartPainter old) => old.progress != progress;
}
