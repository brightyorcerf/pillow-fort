import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/life_grid.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  // TODO: load name/age from SharedPreferences once backend is ready
  String _name = 'tejaansh';
  String _ageStr = '21';

  bool _editName = false;
  bool _editAge = false;

  late final TextEditingController _nameCtrl;
  late final TextEditingController _ageCtrl;

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(text: _name);
    _ageCtrl = TextEditingController(text: _ageStr);
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _ageCtrl.dispose();
    super.dispose();
  }

  int get _age => int.tryParse(_ageStr) ?? 0;

  void _saveName() => setState(() {
        _name = _nameCtrl.text.trim().isNotEmpty
            ? _nameCtrl.text.trim()
            : _name;
        _editName = false;
      });

  void _saveAge() => setState(() {
        _ageStr = _ageCtrl.text.trim().isNotEmpty
            ? _ageCtrl.text.trim()
            : _ageStr;
        _editAge = false;
      });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.cream,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 22),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),

              // ── Header ──────────────────────────────────────────────────
              const Text(
                'Profile',
                style: TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textDark,
                ),
              ),
              const SizedBox(height: 24),

              // ── Name card ───────────────────────────────────────────────
              _editableCard(
                label: 'Name',
                value: _name,
                editing: _editName,
                ctrl: _nameCtrl,
                onEdit: () => setState(() => _editName = true),
                onDone: _saveName,
              ),
              const SizedBox(height: 14),

              // ── Age card ────────────────────────────────────────────────
              _editableCard(
                label: 'Age',
                value: _ageStr,
                editing: _editAge,
                ctrl: _ageCtrl,
                onEdit: () => setState(() => _editAge = true),
                onDone: _saveAge,
                numeric: true,
              ),
              const SizedBox(height: 24),

              // ── Life percentage infographic ─────────────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.creamDark,
                  borderRadius: BorderRadius.circular(22),
                  border:
                      Border.all(color: AppColors.brownBorder, width: 3),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.brownBorder.withOpacity(0.2),
                      offset: const Offset(3, 4),
                      blurRadius: 0,
                    ),
                  ],
                ),
                child: LifeGridWidget(age: _age),
              ),
              const SizedBox(height: 14),

              // Caption
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: Text(
                  '"The gray blocks are gone — they\'re memories.\nThe rest? That\'s ours to build with."',
                  style: const TextStyle(
                    fontFamily: 'DynaPuff',
                    fontSize: 12,
                    color: AppColors.textMedium,
                    height: 1.7,
                  ),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _editableCard({
    required String label,
    required String value,
    required bool editing,
    required TextEditingController ctrl,
    required VoidCallback onEdit,
    required VoidCallback onDone,
    bool numeric = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: cardDecoration(fill: AppColors.sageCard, radius: 22, borderWidth: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: const TextStyle(
                        fontFamily: 'DynaPuff',
                        fontSize: 11,
                        color: AppColors.textMedium)),
                const SizedBox(height: 4),
                editing
                    ? TextField(
                        controller: ctrl,
                        autofocus: true,
                        keyboardType: numeric
                            ? TextInputType.number
                            : TextInputType.text,
                        onSubmitted: (_) => onDone(),
                        style: const TextStyle(
                          fontFamily: 'DynaPuff',
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textDark,
                        ),
                        decoration: const InputDecoration(
                          isDense: true,
                          contentPadding: EdgeInsets.zero,
                          border: InputBorder.none,
                        ),
                      )
                    : Text(value,
                        style: const TextStyle(
                          fontFamily: 'DynaPuff',
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textDark,
                        )),
              ],
            ),
          ),
          GestureDetector(
            onTap: editing ? onDone : onEdit,
            child: Text(
              editing ? 'Done' : 'Edit',
              style: const TextStyle(
                  fontFamily: 'DynaPuff',
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textMedium),
            ),
          ),
        ],
      ),
    );
  }
}
