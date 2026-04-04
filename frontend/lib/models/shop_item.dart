// ---------------------------------------------------------------------------
// models/shop_item.dart
//
// Data layer for the Cosy Shop.
//
// BACKEND INTEGRATION NOTE (for your backend partner):
// ─────────────────────────────────────────────────────
// This file is the SINGLE source of truth for item data.
//
// To connect to a database:
//   1. Keep the [ItemRarity] enum and [ShopItem] class exactly as-is.
//   2. Replace the static [shopItems] and [dailySpecialItem] lists with a
//      service call, e.g.:
//
//        Future<List<ShopItem>> fetchShopItems() async {
//          final response = await http.get(Uri.parse('/api/shop/items'));
//          final data = jsonDecode(response.body) as List;
//          return data.map((e) => ShopItem.fromJson(e)).toList();
//        }
//
//   3. The [ShopItem.fromJson] factory constructor is already wired up below.
//      Just ensure your API returns the matching JSON keys.
// ---------------------------------------------------------------------------

enum ItemRarity { common, rare, legendary }

class ShopItem {
  final String id;         // Unique DB identifier (UUID / slug)
  final String name;
  final String description;
  final int price;
  final ItemRarity rarity;
  final String category;  // 'Snacks' | 'Decor' | 'Special'
  final bool isNew;
  final bool isLimited;
  // imagePath is derived from name: assets/items/<id>.png
  // Override only if your asset naming differs from the id.
  final String? imagePath;

  const ShopItem({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.rarity,
    required this.category,
    this.isNew = false,
    this.isLimited = false,
    this.imagePath,
  });

  /// The resolved path for the item image.
  /// Falls back to the emoji/icon-based card if the asset doesn't exist.
  String get resolvedImagePath => imagePath ?? 'assets/items/$id.png';

  // ── JSON serialization ────────────────────────────────────────────────────

  factory ShopItem.fromJson(Map<String, dynamic> json) => ShopItem(
        id: json['id'] as String,
        name: json['name'] as String,
        description: json['description'] as String,
        price: json['price'] as int,
        rarity: ItemRarity.values.firstWhere(
          (r) => r.name == (json['rarity'] as String).toLowerCase(),
          orElse: () => ItemRarity.common,
        ),
        category: json['category'] as String,
        isNew: (json['is_new'] as bool?) ?? false,
        isLimited: (json['is_limited'] as bool?) ?? false,
        imagePath: json['image_path'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'description': description,
        'price': price,
        'rarity': rarity.name,
        'category': category,
        'is_new': isNew,
        'is_limited': isLimited,
        if (imagePath != null) 'image_path': imagePath,
      };
}

// ---------------------------------------------------------------------------
// Static catalogue — replace with API call when backend is ready.
// ---------------------------------------------------------------------------

const ShopItem dailySpecialItem = ShopItem(
  id: 'kokos_secret_blend',
  name: "Koko's Secret Blend",
  description: 'Only available today. Boosts XP for 24 hours ✨',
  price: 200,
  rarity: ItemRarity.legendary,
  category: 'Special',
);

const List<ShopItem> shopItems = [
  // ── Snacks ────────────────────────────────────────────────────────────────
  ShopItem(
    id: 'matcha_mochi_ball',
    name: 'Matcha Mochi Ball',
    description: 'Restores focus energy and clears mental fog.',
    price: 120,
    rarity: ItemRarity.common,
    category: 'Snacks',
    isNew: true,
  ),
  ShopItem(
    id: 'honey_cloud_cookie',
    name: 'Honey Cloud Cookie',
    description: 'Sweetens study sessions with a gentle XP boost.',
    price: 80,
    rarity: ItemRarity.common,
    category: 'Snacks',
  ),
  ShopItem(
    id: 'cherry_blossom_tea',
    name: 'Cherry Blossom Tea',
    description: 'Calms anxious thoughts and sharpens focus.',
    price: 110,
    rarity: ItemRarity.rare,
    category: 'Snacks',
  ),
  ShopItem(
    id: 'berry_focus_smoothie',
    name: 'Berry Focus Smoothie',
    description: 'Boosts concentration for your next session.',
    price: 100,
    rarity: ItemRarity.common,
    category: 'Snacks',
  ),
  ShopItem(
    id: 'moon_rice_crackers',
    name: 'Moon Rice Crackers',
    description: 'A classic study snack — light and satisfying.',
    price: 60,
    rarity: ItemRarity.common,
    category: 'Snacks',
  ),
  ShopItem(
    id: 'golden_honey_cake',
    name: 'Golden Honey Cake',
    description: 'A legendary reward treat for dedicated scholars.',
    price: 350,
    rarity: ItemRarity.legendary,
    category: 'Snacks',
    isLimited: true,
  ),
  // ── Decor ─────────────────────────────────────────────────────────────────
  ShopItem(
    id: 'tiny_bonsai_pot',
    name: 'Tiny Bonsai Pot',
    description: 'Decorates your sanctuary with calm green energy.',
    price: 150,
    rarity: ItemRarity.rare,
    category: 'Decor',
  ),
  ShopItem(
    id: 'cinnamon_candle',
    name: 'Cinnamon Candle',
    description: 'Warm scented ambiance for long study nights.',
    price: 90,
    rarity: ItemRarity.common,
    category: 'Decor',
  ),
  ShopItem(
    id: 'moon_lamp',
    name: 'Moon Lamp',
    description: 'Soft glow that never strains your eyes.',
    price: 200,
    rarity: ItemRarity.rare,
    category: 'Decor',
  ),
  ShopItem(
    id: 'star_night_poster',
    name: 'Star Night Poster',
    description: 'Pin it up — a reminder to keep reaching higher.',
    price: 70,
    rarity: ItemRarity.common,
    category: 'Decor',
  ),
  // ── Special ───────────────────────────────────────────────────────────────
  ShopItem(
    id: 'focus_ribbon_badge',
    name: 'Focus Ribbon Badge',
    description: 'Wear your dedication with pride.',
    price: 250,
    rarity: ItemRarity.rare,
    category: 'Special',
  ),
  ShopItem(
    id: 'sparkle_aura_pack',
    name: 'Sparkle Aura Pack',
    description: 'Give your mascot a legendary glow-up.',
    price: 400,
    rarity: ItemRarity.legendary,
    category: 'Special',
    isLimited: true,
  ),
];
