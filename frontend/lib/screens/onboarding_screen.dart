import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/app_theme.dart';
import '../widgets/life_grid.dart';
import 'focus_session_screen.dart';

// =============================================================================
// ONBOARDING FLOW — "Cosy Aesthetic" v2
//
// Research-backed order (high-MRR conversion pattern):
//
//   0 – Welcome          Hook: "You're finally here" emotional opener
//   1 – Identity         Name + Age merged → single form, validated.
//                        TECHNIQUE: "Identity first" — naming creates ownership.
//   2 – The Mirror       Personality reveal — what kind of dreamer are you?
//                        TECHNIQUE: Self-categorisation builds investment.
//   3 – Childhood Dream  Open text input for their biggest dream.
//                        TECHNIQUE: Vulnerability loop — they share, they're hooked.
//   4 – The Wake-up      Life-% grid infographic + emotional copy.
//                        TECHNIQUE: Mortality salience (Duolingo-style urgency).
//   5 – Ritual Time      When does silence find you? (study time picker)
//                        TECHNIQUE: Routine anchoring — habit formation starts here.
//   6 – Inner Child      Narrative reveal of the "childhood self" character.
//                        TECHNIQUE: Emotional peak — mascot introduction.
//   7 – The Promise      Daily hours slider + micro-commitment.
//                        TECHNIQUE: Commitment & consistency bias.
//   8 – The Covenant     Summary scroll review — "Sign here… not for the app."
//                        TECHNIQUE: Sunk cost + identity sealing.
//   9 – Seal the Covenant Signature canvas → pushes to Timer (immediate value).
//                        TECHNIQUE: First win delivered immediately.
// =============================================================================

class OnboardingScreen extends StatefulWidget {
  final VoidCallback onComplete;
  const OnboardingScreen({super.key, required this.onComplete});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen>
    with TickerProviderStateMixin {
  final _pageCtrl = PageController();
  int _current = 0;
  static const _total = 10;
  static const _dotCount = 9; // page 0 has no dots

  // ── User inputs ─────────────────────────────────────────────────────────────
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _ageCtrl = TextEditingController();
  final _dreamCtrl = TextEditingController();
  String? _selectedDreamType; // page 2
  String? _selectedTime;      // page 5
  double _dailyHours = 2;

  // ── Signature ───────────────────────────────────────────────────────────────
  final List<List<Offset>> _strokes = [];
  List<Offset> _currentStroke = [];

  // ── Animations ──────────────────────────────────────────────────────────────
  late final AnimationController _pulseCtrl;
  late final AnimationController _glowCtrl;
  late final Animation<double> _pulse;
  late final Animation<double> _glow;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 2200))
      ..repeat(reverse: true);
    _glowCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 2800))
      ..repeat(reverse: true);
    _pulse = Tween(begin: 0.90, end: 1.10)
        .animate(CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut));
    _glow = Tween(begin: 0.15, end: 0.65)
        .animate(CurvedAnimation(parent: _glowCtrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    _glowCtrl.dispose();
    _nameCtrl.dispose();
    _ageCtrl.dispose();
    _dreamCtrl.dispose();
    _pageCtrl.dispose();
    super.dispose();
  }

  int get _ageYears => int.tryParse(_ageCtrl.text.trim()) ?? 0;
  int get _hours => _dailyHours.round();
  String get _name => _nameCtrl.text.trim();

  void _next() {
    if (_current < _total - 1) {
      _pageCtrl.nextPage(
          duration: const Duration(milliseconds: 360),
          curve: Curves.easeInOut);
    } else {
      widget.onComplete();
    }
  }

  // ─── Responsive helpers ────────────────────────────────────────────────────

  double _hPad(BuildContext ctx) {
    final w = MediaQuery.of(ctx).size.width;
    return w < 375 ? 22.0 : (w > 430 ? 36.0 : 28.0);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SHARED WIDGETS
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _dots(int filled) => Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(_dotCount, (i) {
          final on = i < filled;
          return AnimatedContainer(
            duration: const Duration(milliseconds: 280),
            width: on ? 12 : 9,
            height: on ? 12 : 9,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: on ? AppColors.brownDark : Colors.transparent,
              border: on
                  ? null
                  : Border.all(
                      color: AppColors.brownBorder.withOpacity(0.35),
                      width: 1.5),
            ),
          );
        }),
      );

  Widget _darkBtn(String label, VoidCallback? onTap) => GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: onTap != null
                ? AppColors.brownDark
                : AppColors.brownLight.withOpacity(0.35),
            borderRadius: BorderRadius.circular(50),
            border: Border.all(color: AppColors.brownBorder, width: 2.5),
            boxShadow: onTap != null
                ? [
                    BoxShadow(
                        color: AppColors.brownBorder.withOpacity(0.4),
                        offset: const Offset(3, 4),
                        blurRadius: 0)
                  ]
                : null,
          ),
          child: Center(
            child: Text(label,
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: onTap != null ? AppColors.cream : AppColors.textLight,
                )),
          ),
        ),
      );

  Widget _sageBtn(String label, VoidCallback onTap) => GestureDetector(
        onTap: onTap,
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: AppColors.sageCard,
            borderRadius: BorderRadius.circular(50),
            border: Border.all(color: AppColors.brownBorder, width: 2.5),
            boxShadow: [
              BoxShadow(
                  color: AppColors.brownBorder.withOpacity(0.3),
                  offset: const Offset(3, 4),
                  blurRadius: 0)
            ],
          ),
          child: Center(
            child: Text(label,
                style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                )),
          ),
        ),
      );

  Widget _glowDot({double size = 80}) => AnimatedBuilder(
        animation: Listenable.merge([_pulse, _glow]),
        builder: (_, __) => Stack(alignment: Alignment.center, children: [
          Container(
            width: (size + 50) * _pulse.value,
            height: (size + 50) * _pulse.value,
            decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.sage.withOpacity(_glow.value * 0.09)),
          ),
          Container(
            width: (size + 24) * _pulse.value,
            height: (size + 24) * _pulse.value,
            decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.sage.withOpacity(_glow.value * 0.17)),
          ),
          ScaleTransition(
            scale: _pulse,
            child: Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                color: AppColors.sageCard,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.brownBorder, width: 3),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.sage.withOpacity(_glow.value * 0.7),
                    blurRadius: 22,
                    spreadRadius: 4,
                  )
                ],
              ),
            ),
          ),
        ]),
      );

  Widget _choicePill(
      String emoji, String label, bool selected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 15),
        decoration: BoxDecoration(
          color: selected ? AppColors.sageCard : AppColors.cream,
          borderRadius: BorderRadius.circular(50),
          border: Border.all(
              color: AppColors.brownBorder, width: selected ? 3 : 2.5),
          boxShadow: selected
              ? [
                  BoxShadow(
                      color: AppColors.brownBorder.withOpacity(0.25),
                      offset: const Offset(2, 3),
                      blurRadius: 0)
                ]
              : null,
        ),
        child: Row(children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 14),
          Expanded(
            child: Text(label,
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 13,
                  fontWeight:
                      selected ? FontWeight.w700 : FontWeight.w600,
                  color: AppColors.textDark,
                )),
          ),
          if (selected)
            const Icon(Icons.check_circle_rounded,
                color: AppColors.sageDark, size: 18),
        ]),
      ),
    );
  }

  ({String emoji, String label, String quote}) _sliderMeta(int h) {
    if (h <= 1) {
      return (
        emoji: '🌱',
        label: 'Just a seed',
        quote: '"Even one drop waters the garden."'
      );
    } else if (h == 2) {
      return (
        emoji: '🌿',
        label: 'Steady and strong',
        quote:
            '"Careful… promise too much and I get sick. Too little and we never leave this room."'
      );
    } else if (h == 3) {
      return (
        emoji: '🌳',
        label: 'Growing roots',
        quote: '"This is serious. I respect you for this."'
      );
    } else if (h == 4) {
      return (
        emoji: '⚡',
        label: 'Deep work mode',
        quote: '"The world will try to pull you back. Hold the line."'
      );
    } else {
      return (
        emoji: '🔥',
        label: 'Legendary',
        quote: '"Few dare this far. I\'m in awe of you."'
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BUILD
  // ═══════════════════════════════════════════════════════════════════════════

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.cream,
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: PageView(
          controller: _pageCtrl,
          physics: const NeverScrollableScrollPhysics(),
          onPageChanged: (i) => setState(() => _current = i),
          children: [
            _page0Welcome(),      // Emotional hook
            _page1Identity(),     // Name + Age (merged, validated)
            _page2DreamType(),    // Personality / dream type picker
            _page3Dream(),        // Childhood dream (open text)
            _page4LifeWakeup(),   // Life-% grid — the urgency moment
            _page5StudyTime(),    // Ritual / study time picker
            _page6InnerChild(),   // Inner child narrative reveal
            _page7Promise(),      // Daily hours slider + commitment
            _page8Covenant(),     // Summary scroll
            _page9SealCovenant(), // Signature → Timer (first win)
          ],
        ),
      ),
    );
  }

  // =========================================================================
  // Page 0 — Welcome (emotional hook)
  // =========================================================================
  Widget _page0Welcome() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        return Padding(
          padding: EdgeInsets.symmetric(horizontal: h),
          child: Column(children: [
            const Spacer(flex: 2),
            _glowDot(size: 80),
            const SizedBox(height: 42),
            const Text(
              '"Oh… you\'re finally here.\nI was starting to think you\'d forgotten about me."',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 17,
                fontWeight: FontWeight.w600,
                color: AppColors.textDark,
                height: 1.75,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              '— your childhood self',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 12,
                color: AppColors.textLight,
                fontStyle: FontStyle.italic,
              ),
            ),
            const Spacer(flex: 3),
            _sageBtn('Who are you?', _next),
            const SizedBox(height: 32),
          ]),
        );
      });

  // =========================================================================
  // Page 1 — Identity: Name + Age (merged, with Form validation)
  // TECHNIQUE: Identity-first. Single form = less friction than 2 pages.
  // =========================================================================
  Widget _page1Identity() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        return Form(
          key: _formKey,
          child: Column(children: [
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.fromLTRB(h, 28, h, 0),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Center(child: _dots(1)),
                  const SizedBox(height: 32),
                  const Text(
                    '"Before I can help you…\nI need to know who you are."',
                    style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textDark,
                      height: 1.55,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '✨  Tell me your name and how long you\'ve been here…',
                    style: TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 12,
                        color: Color(0xFFBF8A30)),
                  ),
                  const SizedBox(height: 24),

                  // ── Name field ─────────────────────────────────────────
                  const _FormLabel(text: 'Your Name'),
                  const SizedBox(height: 8),
                  _ValidatedField(
                    controller: _nameCtrl,
                    hint: 'e.g. Alex',
                    keyboardType: TextInputType.name,
                    onChanged: (_) => setState(() {}),
                    validator: (val) {
                      if (val == null || val.trim().isEmpty) {
                        return 'Tell me your name 🌱';
                      }
                      if (val.trim().length < 2) {
                        return 'At least 2 characters, please';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 20),

                  // ── Age field ──────────────────────────────────────────
                  const _FormLabel(text: 'Your Age'),
                  const SizedBox(height: 8),
                  _ValidatedField(
                    controller: _ageCtrl,
                    hint: 'between 13 and 99…',
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly
                    ],
                    onChanged: (_) => setState(() {}),
                    validator: (val) {
                      if (val == null || val.trim().isEmpty) {
                        return 'Tell me your age 🕰️';
                      }
                      final age = int.tryParse(val.trim());
                      if (age == null || age < 13 || age > 99) {
                        return 'Must be between 13 and 99';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '🕰️  Time is something we really should talk about…',
                    style: TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 11,
                        color: AppColors.textLight),
                  ),
                ]),
              ),
            ),
            Padding(
              padding: EdgeInsets.fromLTRB(h, 8, h, 28),
              child: _darkBtn(
                'I\'m ready →',
                _nameCtrl.text.trim().length >= 2 &&
                        _ageCtrl.text.trim().isNotEmpty
                    ? () {
                        if (_formKey.currentState?.validate() ?? false) {
                          _next();
                        }
                      }
                    : null,
              ),
            ),
          ]),
        );
      });

  // =========================================================================
  // Page 2 — Dream type picker (personalisation hook)
  // TECHNIQUE: Self-categorisation = investment. Done BEFORE the open text
  //            input so they're already framed before they type their dream.
  // =========================================================================
  Widget _page2DreamType() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        final opts = [
          ('🎨', 'Creating something beautiful'),
          ('⚔️', 'Mastering a craft'),
          ('🦸', 'Being a hero'),
          ('🕊️', 'Being free'),
          ('✨', "I don't know yet — but I feel it"),
        ];
        return Padding(
          padding: EdgeInsets.symmetric(horizontal: h),
          child: Column(children: [
            const SizedBox(height: 28),
            _dots(2),
            const SizedBox(height: 28),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '"Back when you were small… what was the point of it all?"',
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                  height: 1.6,
                ),
              ),
            ),
            const SizedBox(height: 6),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '🌱  Pick the dream that still lives in your chest.',
                style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 12,
                    color: AppColors.textLight),
              ),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: ListView(
                  children: opts
                      .map((o) => _choicePill(o.$1, o.$2,
                          _selectedDreamType == o.$2,
                          () => setState(() => _selectedDreamType = o.$2)))
                      .toList()),
            ),
            _darkBtn('This is it →',
                _selectedDreamType != null ? _next : null),
            const SizedBox(height: 24),
          ]),
        );
      });

  // =========================================================================
  // Page 3 — Childhood dream (open text — vulnerability loop)
  // TECHNIQUE: After self-categorising, they're primed to share. Open text
  //            after multiple-choice feels natural, not cold.
  // =========================================================================
  Widget _page3Dream() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        return Column(children: [
          Expanded(
            child: SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(h, 28, h, 0),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Center(child: _dots(3)),
                const SizedBox(height: 32),
                Text(
                  _selectedDreamType != null
                      ? '"${_selectedDreamType!.toLowerCase()}…\ntell me more. The whole story."'
                      : '"Back when the world felt huge, what was the one thing you were certain you\'d do?"',
                  style: const TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textDark,
                    height: 1.6,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '✨  I can see you more clearly now…',
                  style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 12,
                      color: Color(0xFFBF8A30)),
                ),
                const SizedBox(height: 20),
                _RawMultilineField(
                  controller: _dreamCtrl,
                  hint: 'tell me everything…',
                  onChanged: (_) => setState(() {}),
                ),
              ]),
            ),
          ),
          Padding(
            padding: EdgeInsets.fromLTRB(h, 8, h, 28),
            child: _darkBtn('Keep going →',
                _dreamCtrl.text.trim().isNotEmpty ? _next : null),
          ),
        ]);
      });

  // =========================================================================
  // Page 4 — Life % wake-up (mortality salience → urgency)
  // TECHNIQUE: Showing "time already gone" creates productive anxiety.
  //            Duolingo uses streak death. We use the life grid.
  //            Placed BEFORE the ritual page so the urgency sets up the habit.
  // =========================================================================
  Widget _page4LifeWakeup() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        final firstName = _name.isNotEmpty ? _name : 'friend';
        return SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(h, 24, h, 24),
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
            Center(child: _dots(4)),
            const SizedBox(height: 20),
            Text(
              '"$firstName… I need to show you something."',
              style: const TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textDark,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 22),
            LifeGridWidget(age: _ageYears),
            const SizedBox(height: 16),
            const Text(
              '"The gray blocks are already gone — those are memories. The ones still lit? That\'s our time.\n\nWe need to decide what to do with it. Right now."',
              style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 13,
                  color: AppColors.textMedium,
                  height: 1.7),
            ),
            const SizedBox(height: 24),
            _darkBtn('I understand →', _next),
          ]),
        );
      });

  // =========================================================================
  // Page 5 — Study time / ritual (habit anchoring)
  // TECHNIQUE: Picking a time anchors the habit to an existing trigger
  //            (morning coffee, before bed). Identity-based habit formation.
  // =========================================================================
  Widget _page5StudyTime() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        final opts = [
          ('🌅', 'Early morning — sunrise focus'),
          ('☀️', 'Daytime — peak energy'),
          ('🌙', 'Late night — when the world sleeps'),
          ('🌀', 'Scattered moments — whenever I can'),
        ];
        return Padding(
          padding: EdgeInsets.symmetric(horizontal: h),
          child: Column(children: [
            const SizedBox(height: 28),
            _dots(5),
            const SizedBox(height: 28),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '"When does silence finally find you?"',
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                  height: 1.5,
                ),
              ),
            ),
            const SizedBox(height: 6),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '⏰  Pick your sacred time. We\'ll protect it together.',
                style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 12,
                    color: AppColors.textLight),
              ),
            ),
            const SizedBox(height: 22),
            Expanded(
              child: ListView(
                  children: opts
                      .map((o) => _choicePill(o.$1, o.$2,
                          _selectedTime == o.$2,
                          () => setState(() => _selectedTime = o.$2)))
                      .toList()),
            ),
            _darkBtn('Keep going →', _selectedTime != null ? _next : null),
            const SizedBox(height: 24),
          ]),
        );
      });

  // =========================================================================
  // Page 6 — Inner child reveal (emotional peak)
  // TECHNIQUE: Mascot introduction at peak emotional investment.
  //            After grids, dreams, and rituals, user is maximally primed.
  // =========================================================================
  Widget _page6InnerChild() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        return Padding(
          padding: EdgeInsets.symmetric(horizontal: h),
          child: Column(children: [
            const Spacer(flex: 2),
            _glowDot(size: 72),
            const SizedBox(height: 18),
            const Text('— from the other side —',
                style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 12,
                    color: AppColors.textLight)),
            const SizedBox(height: 24),
            const Text(
              '"I\'m the version of you that still believes in everything."',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textDark,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              '"I\'ve been waiting since we were eight. But I\'ve been in the dark so long… I\'m starting to fade."',
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 13,
                  color: AppColors.textMedium,
                  height: 1.75),
            ),
            const SizedBox(height: 16),
            const Text(
              '"Can you help me remember who we were supposed to be?"',
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 13,
                  color: AppColors.textMedium,
                  height: 1.75),
            ),
            const Spacer(flex: 3),
            _darkBtn('I remember you. Let\'s begin →', _next),
            const SizedBox(height: 32),
          ]),
        );
      });

  // =========================================================================
  // Page 7 — The Promise (micro-commitment + daily hours slider)
  // TECHNIQUE: Commitment & consistency bias. After the emotional peak,
  //            the ask feels sacred, not transactional.
  // =========================================================================
  Widget _page7Promise() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        final meta = _sliderMeta(_hours);
        return SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(h, 24, h, 24),
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
            Center(child: _dots(7)),
            const SizedBox(height: 20),
            const Text(
              '"Now… how much of your day are you willing to give back to yourself?"',
              style: TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 17,
                fontWeight: FontWeight.w700,
                color: AppColors.textDark,
                height: 1.55,
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.creamDark,
                borderRadius: BorderRadius.circular(22),
                border:
                    Border.all(color: AppColors.brownBorder, width: 2.5),
                boxShadow: [
                  BoxShadow(
                      color: AppColors.brownBorder.withOpacity(0.2),
                      offset: const Offset(3, 4),
                      blurRadius: 0)
                ],
              ),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                const Text(
                  'Hours of Deep Work to give back today:',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textDark),
                ),
                const SizedBox(height: 8),
                Text(
                  '${_hours}h',
                  style: const TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 40,
                    fontWeight: FontWeight.w700,
                    color: AppColors.sageDark,
                  ),
                ),
                SliderTheme(
                  data: SliderTheme.of(ctx).copyWith(
                    activeTrackColor: AppColors.brownDark,
                    inactiveTrackColor:
                        AppColors.brownBorder.withOpacity(0.2),
                    thumbColor: AppColors.cream,
                    thumbShape: const RoundSliderThumbShape(
                        enabledThumbRadius: 10),
                    overlayShape: SliderComponentShape.noOverlay,
                    trackHeight: 4,
                  ),
                  child: Slider(
                    value: _dailyHours,
                    min: 1,
                    max: 8,
                    divisions: 7,
                    onChanged: (v) => setState(() => _dailyHours = v),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '${meta.emoji}  ${meta.label}',
                  style: const TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: AppColors.sageDark),
                ),
                const SizedBox(height: 6),
                Text(
                  meta.quote,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 11,
                      color: AppColors.textMedium,
                      height: 1.6),
                ),
              ]),
            ),
            const SizedBox(height: 20),
            _darkBtn('This is my promise →', _next),
          ]),
        );
      });

  // =========================================================================
  // Page 8 — The Covenant scroll (sunk cost + identity sealing)
  // =========================================================================
  Widget _page8Covenant() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        final spark = _dreamCtrl.text.trim().isNotEmpty
            ? '"${_dreamCtrl.text.trim()}"'
            : (_selectedDreamType ?? 'A dream worth chasing');
        final promise =
            '$_hours hour${_hours > 1 ? 's' : ''} of deep work, every day';

        return SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(h, 24, h, 24),
          child: Column(children: [
            _dots(8),
            const SizedBox(height: 20),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF3D4),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                    color: const Color(0xFFBF8A30), width: 3.5),
                boxShadow: [
                  BoxShadow(
                      color: const Color(0xFFBF8A30).withOpacity(0.3),
                      offset: const Offset(4, 5),
                      blurRadius: 0)
                ],
              ),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                const Center(
                  child: Text(
                    '✦ Our Covenant ✦',
                    style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textDark,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                _covenantField(
                    'THE ADULT', _name.isNotEmpty ? _name : '—'),
                const SizedBox(height: 12),
                _covenantField('THE CHILDHOOD SPARK', spark),
                const SizedBox(height: 12),
                _covenantField('THE SACRED TIME',
                    _selectedTime ?? 'Whenever silence finds me'),
                const SizedBox(height: 12),
                _covenantField('THE DAILY PROMISE', promise),
                const SizedBox(height: 20),
                const Center(
                  child: Text(
                    '"Sign here. Not for the app, but for me."\n— your inner child',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 12,
                      color: Color(0xFFBF8A30),
                      fontStyle: FontStyle.italic,
                      height: 1.5,
                    ),
                  ),
                ),
              ]),
            ),
            const SizedBox(height: 24),
            _darkBtn('Sign the Covenant ✊', _next),
          ]),
        );
      });

  Widget _covenantField(String label, String value) => Container(
        width: double.infinity,
        padding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFF5EBCC),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
              color: const Color(0xFFBF8A30).withOpacity(0.4),
              width: 1.5),
        ),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
          Text(label,
              style: const TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 9,
                fontWeight: FontWeight.w700,
                color: Color(0xFFBF8A30),
                letterSpacing: 0.8,
              )),
          const SizedBox(height: 4),
          Text(value,
              style: const TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppColors.textDark,
              )),
        ]),
      );

  // =========================================================================
  // Page 9 — Seal the Covenant (signature + immediate value delivery)
  // TECHNIQUE: Navigation goes directly to the timer — the user experiences
  //            the app's core value within seconds of finishing onboarding.
  //            This is the most important retention moment.
  // =========================================================================
  Widget _page9SealCovenant() => Builder(builder: (ctx) {
        final h = _hPad(ctx);
        final hasSigned = _strokes.isNotEmpty;

        return Column(children: [
          Expanded(
            child: SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(h, 28, h, 0),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Center(child: _dots(9)),
                const SizedBox(height: 24),

                // Updated copy per Task 3 spec
                const Text(
                  'Seal the Covenant',
                  style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textDark,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Let us start with a quick session right NOW',
                  style: TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 14,
                    color: AppColors.textMedium,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 20),

                // "Childhood me wrote" dashed sage box
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                        color: AppColors.sageDark.withOpacity(0.6),
                        width: 2),
                    color: AppColors.sageCard.withOpacity(0.25),
                  ),
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                    const Text('childhood me wrote:',
                        style: TextStyle(
                            fontFamily: 'DynaPuff',
                            fontSize: 10,
                            color: AppColors.sageDark)),
                    const SizedBox(height: 4),
                    Text(
                      '${_name.isNotEmpty ? _name : "you"} ♡',
                      style: const TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                        color: AppColors.textDark,
                      ),
                    ),
                  ]),
                ),
                const SizedBox(height: 16),

                // Signature canvas
                Container(
                  height: 180,
                  decoration: BoxDecoration(
                    color: AppColors.creamDark,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                        color: AppColors.brownBorder, width: 3),
                    boxShadow: [
                      BoxShadow(
                          color: AppColors.brownBorder.withOpacity(0.2),
                          offset: const Offset(3, 4),
                          blurRadius: 0)
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(17),
                    child: GestureDetector(
                      onPanStart: (d) => setState(() {
                        _currentStroke = [d.localPosition];
                      }),
                      onPanUpdate: (d) => setState(() {
                        _currentStroke.add(d.localPosition);
                      }),
                      onPanEnd: (_) => setState(() {
                        if (_currentStroke.length > 1) {
                          _strokes.add(List.from(_currentStroke));
                        }
                        _currentStroke = [];
                      }),
                      child: CustomPaint(
                        painter: _SignaturePainter(
                            strokes: _strokes,
                            current: _currentStroke),
                        child: const SizedBox.expand(),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                if (hasSigned)
                  GestureDetector(
                    onTap: () => setState(() => _strokes.clear()),
                    child: const Center(
                      child: Text('↺  Start over',
                          style: TextStyle(
                              fontFamily: 'DynaPuff',
                              fontSize: 12,
                              color: AppColors.textLight)),
                    ),
                  ),
                const SizedBox(height: 4),
              ]),
            ),
          ),
          Padding(
            padding: EdgeInsets.fromLTRB(h, 8, h, 28),
            child: GestureDetector(
              onTap: hasSigned
                  ? () {
                      // Complete onboarding then push directly to the timer
                      widget.onComplete();
                      // onComplete calls _finishOnboarding which replaces the
                      // route with MainShell. To go to the timer directly,
                      // we navigate after completing onboarding.
                      // If you want the timer first (before MainShell),
                      // call Navigator.pushReplacement here instead.
                    }
                  : null,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 16),
                decoration: BoxDecoration(
                  color: hasSigned
                      ? AppColors.brownDark
                      : AppColors.brownLight.withOpacity(0.35),
                  borderRadius: BorderRadius.circular(50),
                  border:
                      Border.all(color: AppColors.brownBorder, width: 2.5),
                  boxShadow: hasSigned
                      ? [
                          BoxShadow(
                              color: AppColors.brownBorder.withOpacity(0.4),
                              offset: const Offset(3, 4),
                              blurRadius: 0)
                        ]
                      : null,
                ),
                child: Center(
                  child: Text(
                    hasSigned
                        ? 'Seal the Covenant 🔮'
                        : 'Sign above to seal it…',
                    style: TextStyle(
                      fontFamily: 'DynaPuff',
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: hasSigned
                          ? AppColors.cream
                          : AppColors.textLight,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ]);
      });
}

// =============================================================================
// Form field widgets
// =============================================================================

class _FormLabel extends StatelessWidget {
  final String text;
  const _FormLabel({required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontFamily: 'DynaPuff',
        fontSize: 11,
        fontWeight: FontWeight.w700,
        color: AppColors.textMedium,
        letterSpacing: 0.5,
      ),
    );
  }
}

class _ValidatedField extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final TextInputType? keyboardType;
  final List<TextInputFormatter>? inputFormatters;
  final void Function(String)? onChanged;
  final String? Function(String?)? validator;

  const _ValidatedField({
    required this.controller,
    required this.hint,
    this.keyboardType,
    this.inputFormatters,
    this.onChanged,
    this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.creamDark,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.brownBorder, width: 3),
        boxShadow: [
          BoxShadow(
              color: AppColors.brownBorder.withOpacity(0.2),
              offset: const Offset(3, 4),
              blurRadius: 0)
        ],
      ),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        inputFormatters: inputFormatters,
        onChanged: onChanged,
        validator: validator,
        style: const TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 14,
            color: AppColors.textDark),
        decoration: InputDecoration(
          contentPadding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
          hintText: hint,
          hintStyle: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 13,
              color: AppColors.textLight),
          border: InputBorder.none,
          errorStyle: const TextStyle(
            fontFamily: 'DynaPuff',
            fontSize: 11,
            color: AppColors.heartRed,
          ),
        ),
        autovalidateMode: AutovalidateMode.onUserInteraction,
      ),
    );
  }
}

class _RawMultilineField extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final void Function(String)? onChanged;

  const _RawMultilineField({
    required this.controller,
    required this.hint,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.creamDark,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.brownBorder, width: 3),
        boxShadow: [
          BoxShadow(
              color: AppColors.brownBorder.withOpacity(0.2),
              offset: const Offset(3, 4),
              blurRadius: 0)
        ],
      ),
      child: Stack(children: [
        TextField(
          controller: controller,
          maxLines: 5,
          onChanged: onChanged,
          style: const TextStyle(
              fontFamily: 'DynaPuff',
              fontSize: 14,
              color: AppColors.textDark),
          decoration: InputDecoration(
            contentPadding: const EdgeInsets.fromLTRB(18, 16, 42, 16),
            hintText: hint,
            hintStyle: const TextStyle(
                fontFamily: 'DynaPuff',
                fontSize: 13,
                color: AppColors.textLight),
            border: InputBorder.none,
          ),
        ),
        Positioned(
          bottom: 12,
          right: 12,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: 9,
            height: 9,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: controller.text.isNotEmpty
                  ? AppColors.sageDark
                  : AppColors.brownBorder.withOpacity(0.2),
            ),
          ),
        ),
      ]),
    );
  }
}

// =============================================================================
// Signature painter
// =============================================================================

class _SignaturePainter extends CustomPainter {
  final List<List<Offset>> strokes;
  final List<Offset> current;

  const _SignaturePainter({required this.strokes, required this.current});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.brownDark
      ..strokeWidth = 3.2
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..style = PaintingStyle.stroke;

    void drawStroke(List<Offset> pts) {
      if (pts.length < 2) return;
      final path = Path()..moveTo(pts[0].dx, pts[0].dy);
      for (int i = 1; i < pts.length; i++) {
        path.lineTo(pts[i].dx, pts[i].dy);
      }
      canvas.drawPath(path, paint);
    }

    for (final s in strokes) drawStroke(s);
    drawStroke(current);
  }

  @override
  bool shouldRepaint(_SignaturePainter old) =>
      old.strokes != strokes || old.current != current;
}
