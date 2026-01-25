"""
Management command to seed theme presets from the UI library.

Usage:
    python manage.py seed_theme_presets
    python manage.py seed_theme_presets --reset  # Clear and reseed
"""

from django.core.management.base import BaseCommand
from apps.tenants.models import Theme
import json


# Theme preset definitions from UI library
# These match the themes defined in ui/src/theme/presets/

DEFAULT_THEME = {
    "meta": {
        "id": "default",
        "name": "Default",
        "version": "1.0.0",
        "category": "official",
        "description": "Clean, professional light theme with neutral colors",
        "tags": ["light", "neutral", "professional"]
    },
    "tokens": {
        "colors": {
            "primary": "#0066cc",
            "primaryMuted": "#e6f2ff",
            "secondary": "#6b7280",
            "secondaryMuted": "#f3f4f6",
            "success": "#10b981",
            "successMuted": "#d1fae5",
            "warning": "#f59e0b",
            "warningMuted": "#fef3c7",
            "error": "#ef4444",
            "errorMuted": "#fee2e2",
            "info": "#0ea5e9",
            "infoMuted": "#e0f2fe",
            "background": "#ffffff",
            "backgroundSecondary": "#f9fafb",
            "backgroundTertiary": "#f3f4f6",
            "surface": "#ffffff",
            "textPrimary": "#111827",
            "textSecondary": "#6b7280",
            "textTertiary": "#9ca3af",
            "textDisabled": "#d1d5db",
            "textOnPrimary": "#ffffff",
            "textOnSecondary": "#ffffff",
            "border": "#e5e7eb",
            "borderFocus": "#0066cc",
            "disabled": "#f3f4f6",
            "focus": "#0066cc",
            "overlay": "rgba(0, 0, 0, 0.5)"
        },
        "typography": {
            "fontFamily": {
                "primary": "-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif",
                "secondary": "Georgia, \"Times New Roman\", serif",
                "monospace": "\"SF Mono\", Monaco, \"Cascadia Code\", \"Roboto Mono\", Consolas, \"Courier New\", monospace"
            },
            "fontSize": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
                "4xl": "2.25rem",
                "5xl": "3rem"
            },
            "fontWeight": {
                "light": 300,
                "normal": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            },
            "lineHeight": {
                "tight": 1.25,
                "normal": 1.5,
                "relaxed": 1.75,
                "loose": 2.0
            }
        },
        "spacing": {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
            "2xl": "3rem",
            "3xl": "4rem",
            "4xl": "6rem",
            "5xl": "8rem"
        },
        "radius": {
            "none": "0",
            "sm": "0.25rem",
            "md": "0.375rem",
            "lg": "0.5rem",
            "xl": "0.75rem",
            "2xl": "1rem",
            "full": "9999px"
        },
        "shadows": {
            "none": "none",
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
        },
        "motion": {
            "duration": {
                "instant": 75,
                "fast": 150,
                "normal": 300,
                "slow": 500,
                "slower": 800
            },
            "easing": {
                "linear": "linear",
                "easeIn": "cubic-bezier(0.4, 0, 1, 1)",
                "easeOut": "cubic-bezier(0, 0, 0.2, 1)",
                "easeInOut": "cubic-bezier(0.4, 0, 0.2, 1)"
            }
        },
        "breakpoints": {
            "xs": 0,
            "sm": 640,
            "md": 768,
            "lg": 1024,
            "xl": 1280,
            "2xl": 1536
        },
        "zIndex": {
            "base": 0,
            "dropdown": 1000,
            "sticky": 1100,
            "modal": 1200,
            "popover": 1300,
            "tooltip": 1400,
            "toast": 1600
        }
    },
    "modes": {
        "dark": {
            "name": "dark",
            "label": "Dark Mode",
            "tokens": {
                "colors": {
                    "primary": "#3b82f6",
                    "primaryMuted": "#1e3a8a",
                    "background": "#111827",
                    "backgroundSecondary": "#1f2937",
                    "backgroundTertiary": "#374151",
                    "surface": "#1f2937",
                    "textPrimary": "#f9fafb",
                    "textSecondary": "#d1d5db",
                    "textTertiary": "#9ca3af",
                    "border": "#374151",
                    "borderFocus": "#3b82f6"
                }
            }
        }
    }
}

DARK_THEME = {
    "meta": {
        "id": "dark",
        "name": "Dark",
        "version": "1.0.0",
        "category": "official",
        "description": "Modern dark theme optimized for low-light environments",
        "tags": ["dark", "modern", "low-light"]
    },
    "tokens": DEFAULT_THEME["tokens"].copy(),
    "modes": {
        "light": {
            "name": "light",
            "label": "Light Mode",
            "tokens": {
                "colors": DEFAULT_THEME["tokens"]["colors"].copy()
            }
        }
    }
}

# Update dark theme base colors
DARK_THEME["tokens"]["colors"].update({
    "primary": "#3b82f6",
    "primaryMuted": "#1e3a8a",
    "background": "#0f172a",
    "backgroundSecondary": "#1e293b",
    "backgroundTertiary": "#334155",
    "surface": "#1e293b",
    "textPrimary": "#f1f5f9",
    "textSecondary": "#cbd5e1",
    "textTertiary": "#94a3b8",
    "textDisabled": "#64748b",
    "textOnPrimary": "#ffffff",
    "textOnSecondary": "#0f172a",
    "border": "#334155",
    "borderFocus": "#3b82f6",
    "disabled": "#334155",
    "focus": "#3b82f6",
    "overlay": "rgba(0, 0, 0, 0.8)"
})

BRAND_LIGHT_THEME = {
    "meta": {
        "id": "brand-light",
        "name": "Brand Light",
        "version": "1.0.0",
        "category": "official",
        "description": "Vibrant brand-focused theme with purple and pink accents",
        "tags": ["light", "brand", "vibrant", "marketing"]
    },
    "tokens": DEFAULT_THEME["tokens"].copy(),
    "modes": {}
}

BRAND_LIGHT_THEME["tokens"]["colors"].update({
    "primary": "#7c3aed",
    "primaryMuted": "#ede9fe",
    "secondary": "#ec4899",
    "secondaryMuted": "#fce7f3",
    "background": "#ffffff",
    "backgroundSecondary": "#faf5ff",
    "backgroundTertiary": "#f5f3ff",
    "border": "#e9d5ff",
    "borderFocus": "#7c3aed",
    "focus": "#7c3aed",
    "overlay": "rgba(124, 58, 237, 0.3)"
})

BRAND_DARK_THEME = {
    "meta": {
        "id": "brand-dark",
        "name": "Brand Dark",
        "version": "1.0.0",
        "category": "official",
        "description": "Dark brand theme with purple and pink accents",
        "tags": ["dark", "brand", "vibrant", "marketing"]
    },
    "tokens": DEFAULT_THEME["tokens"].copy(),
    "modes": {}
}

BRAND_DARK_THEME["tokens"]["colors"].update({
    "primary": "#a78bfa",
    "primaryMuted": "#4c1d95",
    "secondary": "#f472b6",
    "secondaryMuted": "#831843",
    "background": "#1e1b4b",
    "backgroundSecondary": "#312e81",
    "backgroundTertiary": "#3730a3",
    "surface": "#312e81",
    "textPrimary": "#f5f3ff",
    "textSecondary": "#ddd6fe",
    "textTertiary": "#c4b5fd",
    "textDisabled": "#a78bfa",
    "textOnPrimary": "#1e1b4b",
    "textOnSecondary": "#1e1b4b",
    "border": "#4338ca",
    "borderFocus": "#a78bfa",
    "disabled": "#3730a3",
    "focus": "#a78bfa",
    "overlay": "rgba(124, 58, 237, 0.7)"
})

# Preset themes registry
PRESET_THEMES = [
    DEFAULT_THEME,
    DARK_THEME,
    BRAND_LIGHT_THEME,
    BRAND_DARK_THEME,
]


class Command(BaseCommand):
    help = 'Seed theme presets from UI library'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear existing presets before seeding',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)

        if reset:
            self.stdout.write('Clearing existing preset themes...')
            deleted_count = Theme.objects.filter(is_preset=True).delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} preset themes'))

        self.stdout.write('Seeding theme presets...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for theme_data in PRESET_THEMES:
            meta = theme_data['meta']
            theme_id = meta['id']
            theme_name = meta['name']
            theme_version = meta['version']

            # Check if preset already exists
            existing = Theme.objects.filter(
                is_preset=True,
                name=theme_name
            ).first()

            if existing:
                # Update if version changed or reset flag is set
                if existing.version != theme_version or reset:
                    existing.version = theme_version
                    existing.theme_json = theme_data
                    existing.save()
                    updated_count += 1
                    self.stdout.write(f'  Updated: {theme_name} v{theme_version}')
                else:
                    skipped_count += 1
                    self.stdout.write(f'  Skipped: {theme_name} v{theme_version} (already exists)')
            else:
                # Create new preset
                Theme.objects.create(
                    name=theme_name,
                    version=theme_version,
                    is_preset=True,
                    theme_json=theme_data,
                    tenant=None,
                    created_by=None
                )
                created_count += 1
                self.stdout.write(f'  Created: {theme_name} v{theme_version}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete: {created_count} created, {updated_count} updated, {skipped_count} skipped'
            )
        )
        
        # List all presets
        self.stdout.write('\nAvailable theme presets:')
        for theme in Theme.objects.filter(is_preset=True).order_by('name'):
            self.stdout.write(f'  • {theme.name} v{theme.version}')
