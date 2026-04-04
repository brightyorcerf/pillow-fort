# pillow fort  

Cosy productivity app. 

- lock the goal and sign the Convenant scroll 
- achieve goals everyday
- check stats to track progress
- spoil your childhood version with snacks and accessories!
- if you don't perform, the childhood version within you dies :(

Tech Stack / tools: Flutter, Dart, Rive, Figma

## Frontend Setup
```
cd frontend
```

#### Get DynaPuff font
Download from [Google Fonts](https://fonts.google.com/specimen/DynaPuff) and place the `.ttf` files in:
```
assets/fonts/ 
``` 

#### Install dependencies
```bash
flutter pub get
```

#### Run
```bash
flutter run

# command to host it on local ip network 
# so you can open http://IP_address:8080 on phone and test)
flutter run -d web-server --web-port 8080 --web-hostname 0.0.0.0
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

## Integrating Rive Mascot

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