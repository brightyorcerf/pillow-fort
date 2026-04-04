# 🌿 Your Sanctuary — Flutter Frontend

Cosy productivity app. Flutter-only frontend, ready for backend integration.

## Project Structure

```
lib/
├── main.dart                    # App entry, bottom nav shell
├── theme/
│   └── app_theme.dart           # Colors, theme, shared card decoration
├── screens/
│   ├── sanctuary_screen.dart    # Home screen with mascot + focus button
│   ├── focus_session_screen.dart# Timer screen (25min default, editable)
│   ├── progress_screen.dart     # Stats + animated chart + 30-day grid
│   └── placeholder_screens.dart # Shop + Profile (stubs)
└── widgets/
    └── app_nav_bar.dart         # Bottom navigation bar
```

## Setup

### 1. Get DynaPuff font
Download from [Google Fonts](https://fonts.google.com/specimen/DynaPuff) and place the `.ttf` files in:
```
assets/fonts/
  DynaPuff-Regular.ttf
  DynaPuff-Medium.ttf
  DynaPuff-SemiBold.ttf
  DynaPuff-Bold.ttf
```
Create the directory first: `mkdir -p assets/fonts`

### 2. Install dependencies
```bash
flutter pub get
```

### 3. Run
```bash
flutter run
```

---

## Design Tokens (from `app_theme.dart`)

| Token | Hex | Usage |
|---|---|---|
| `cream` | `#F5F0E8` | Background |
| `sageCard` | `#B8C9AB` | Card fill |
| `brownDark` | `#2C1F14` | Primary text, buttons |
| `brownBorder` | `#3D2B1F` | All borders, shadows |
| `heartRed` | `#E85555` | Hearts, missed days |

---

## Integrating Your Rive Mascot

1. Add `rive: ^0.12.4` to `pubspec.yaml` dependencies
2. Place your `.riv` file at `assets/rive/mascot.riv`
3. Uncomment the asset in `pubspec.yaml`
4. In `sanctuary_screen.dart`, replace the placeholder icon with:
```dart
import 'package:rive/rive.dart';

// Inside the circle container:
child: RiveAnimation.asset(
  'assets/rive/mascot.riv',
  fit: BoxFit.contain,
),
```

---

## Backend Integration Points

All backend hooks are marked with `// TODO: connect to backend` comments.

| Screen | Data to fetch |
|---|---|
| `SanctuaryScreen` | Hearts count, today's studied hours |
| `ProgressScreen` | Total hours, streak, sessions, focus rate, weekly data, 30-day activity |
| `FocusSessionScreen` | POST completed session on timer end |

Replace the mock constants at the top of each screen with your API calls.

---

## 30-Day Activity Grid

- **Studied day** → sage green cell, shows hours (e.g. `2.5`)
- **Missed day** → red-tinted cell with day number
- **Future day** → greyed out

Intensity of green scales with hours studied (up to 6h = full intensity).

command to host it on local ip network (you can open http://IP_address:8080 on phone)
flutter run -d web-server --web-port 8080 --web-hostname 0.0.0.0