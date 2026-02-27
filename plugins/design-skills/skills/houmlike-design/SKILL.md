---
name: houmlike-design
description: Create web UI, interfaces, landing pages, and design artifacts for Houm, a maternity care service provider. This skill should be used when designing or building any visual or interactive elements for Houm's digital presence, applying Houm's brand identity, values, and design philosophy.
license: Complete terms in LICENSE.txt
---

# Houmlike Design

To create designs and interfaces for Houm, use this skill. Houm is a maternity care service provider committed to transforming the maternity care experience through informed consent, evidence-based care, companion support, and mindful intervention.

---

## Canonical Design System

**This section defines THE standard. Use these values for consistency across all Houm properties.**

### Canonical Typography

| Role | Font | Fallback | Usage |
|------|------|----------|-------|
| **Headings** | Libre Baskerville | Georgia, serif | All headings (h1-h6), hero text |
| **Body** | Lato | system-ui, sans-serif | Body text, UI elements, buttons |

**Font Loading (Web):**
```html
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Lato:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**CSS Variables:**
```css
:root {
  --font-serif: 'Libre Baskerville', Georgia, serif;
  --font-sans: 'Lato', system-ui, sans-serif;
}
```

**Tailwind Config:**
```javascript
fontFamily: {
  serif: ['Libre Baskerville', 'Georgia', 'serif'],
  sans: ['Lato', 'system-ui', 'sans-serif'],
}
```

### Canonical Colors

**Primary Palette - Green (Action & Health):**

| Name | Hex | HSL | Usage |
|------|-----|-----|-------|
| Primary | `#668e67` | `hsl(122 16% 48%)` | Primary buttons, key accents |
| Primary Dark | `#4b7a4c` | `hsl(121 24% 39%)` | Hover states, headers |
| Primary Light | `#B8D4B9` | `hsl(122 30% 78%)` | Highlights, tags |

**Warm Accent Palette - Terracotta (Nurturing & Warmth):**

| Name | Hex | HSL | Usage |
|------|-----|-----|-------|
| Terracotta | `#CCA893` | `hsl(22 33% 69%)` | Warm accents, soft highlights, nurturing elements |
| Terracotta Dark | `#B8927A` | `hsl(22 33% 60%)` | Hover states for terracotta elements |
| Terracotta Light | `#E8D4C4` | `hsl(22 40% 84%)` | Subtle warm backgrounds, gentle emphasis |

> **Design Intent:** Terracotta adds warmth and a nurturing feel that complements the cream background. Use it for elements that should feel soft and personal (welcome messages, comfort-related features) rather than action-oriented. Green remains the primary action color for buttons and CTAs.

**Neutral Palette:**

| Name | Hex | HSL | Usage |
|------|-----|-----|-------|
| Background | `#F9F7F2` | `hsl(43 38% 96%)` | Page backgrounds |
| Background Dark | `#EDE8DD` | `hsl(43 30% 89%)` | Card backgrounds, sections |
| Text | `#1F2937` | `hsl(220 13% 18%)` | Body text |
| Text Muted | `#6B7280` | `hsl(220 9% 46%)` | Secondary text |

**Color Relationship:**
```
Green (Action)     ←→     Terracotta (Warmth)
    ↓                           ↓
Professional               Nurturing
Health/Growth              Comfort/Care
Buttons/CTAs               Accents/Highlights
    ↓                           ↓
            Cream Background
            (Unifies both)
```

**CSS Variables (recommended):**
```css
:root {
  /* Primary Green - Action color */
  --houm-primary-h: 122;
  --houm-primary-s: 16%;
  --houm-primary-l: 48%;
  --houm-primary: hsl(var(--houm-primary-h) var(--houm-primary-s) var(--houm-primary-l));
  --houm-primary-dark: hsl(121 24% 39%);
  --houm-primary-light: hsl(122 30% 78%);

  /* Terracotta - Warm accent */
  --houm-warm: hsl(22 33% 69%);
  --houm-warm-dark: hsl(22 33% 60%);
  --houm-warm-light: hsl(22 40% 84%);

  /* Neutrals */
  --houm-bg: hsl(43 38% 96%);
  --houm-bg-dark: hsl(43 30% 89%);
  --houm-text: hsl(220 13% 18%);
  --houm-text-muted: hsl(220 9% 46%);
}
```

### Canonical Spacing & Radius

| Element | Border Radius | Notes |
|---------|---------------|-------|
| Buttons | `rounded-xl` (12px) | Consistent across all buttons |
| Cards | `rounded-2xl` (16px) | Slightly softer for containers |
| Inputs | `rounded-lg` (8px) | Compact, functional feel |
| Avatars | `rounded-full` | Always circular |

### Canonical Shadows

```css
--shadow-soft: 0 2px 8px rgba(0, 0, 0, 0.08);
--shadow-medium: 0 4px 16px rgba(0, 0, 0, 0.12);
--shadow-glow: 0 0 20px rgba(102, 142, 103, 0.15);  /* Green-tinted */
```

---

## When to Use This Skill

Use this skill when:
- Designing web UI or interfaces for Houm services
- Creating landing pages or marketing materials for Houm
- Building React-based web applications for Houm
- Designing static visual materials (posters, graphics, PDFs)
- Creating internal tools or dashboards for Houm staff
- Any design work that should reflect Houm's brand identity

## Houm's Brand Identity

### Core Values

Houm's design should reflect these guiding principles:

1. **Full and Informed Consent on Birth** - Designs should promote transparency, clear communication, and understanding. Use clear information hierarchy, readable typography, and intuitive navigation.

2. **Holistic Evidence-Based Approach** - Designs should feel professional, trustworthy, and grounded. Use structured layouts, credible visual language, and evidence-based design patterns.

3. **Team up with Companions** - Designs should feel collaborative, warm, and supportive. Use inclusive imagery, friendly interactions, and partnership-focused messaging.

4. **Pay Close Attention to Intervention** - Designs should be thoughtful, intentional, and natural. Avoid over-design; embrace simplicity and purposeful choices.

### Brand Colors

**Primary Palette (Greens) - Action & Health:**
Houm's identity centers on calming, natural green tones representing growth, health, and nurturing care.

- Dark Green: `#4b7a4c` - Primary text, strong accents, headers
- Forest Green: `#668e67` - Primary buttons, key elements
- Sage Green: `#789b78` - Secondary elements, borders
- Medium Green: `#8aa88a` - Tertiary accents
- Light Green: `#81a282` - Hover states, active elements
- Soft Green: `#98b298` - Backgrounds, subtle sections
- Pale Green: `#a5bca5` - Light backgrounds
- Mint: `#c9d7c9` - Very light backgrounds
- Ice Green: `#e4ebe4` - Subtle dividers, cards

**Warm Accent Palette (Terracotta) - Nurturing & Comfort:**
Terracotta tones add warmth and a nurturing feel, blending naturally with the cream background.

- Terracotta: `#CCA893` - Warm accents, soft highlights, welcome elements
- Terracotta Dark: `#B8927A` - Hover states, emphasis
- Terracotta Light: `#E8D4C4` - Subtle warm backgrounds

**Neutral Palette:**

- Background Cream: `#F9F7F2` - **Canonical** page background
- Warm Cream: `#f5efdf` - Alternative warm background (legacy)
- Pure White: `#ffffff` - Clean card backgrounds
- Soft White: `#f6f8f6` - Alternative light backgrounds

**Usage Guidelines:**
- **Green for action**: Buttons, CTAs, progress indicators, health-related elements
- **Terracotta for warmth**: Welcome messages, comfort features, nurturing content, soft accents
- Use darker greens (#4b7a4c, #668e67) for text and primary actions
- Use terracotta (#CCA893) sparingly for warmth, not as primary action color
- Use lighter greens (#98b298, #a5bca5, #c9d7c9, #e4ebe4) for backgrounds and subtle divisions
- Use cream (#F9F7F2) as the standard page background
- Maintain high contrast for accessibility (WCAG AA minimum)

**Color Pairing Examples:**
- Hero section: Cream background + Green CTA button + Terracotta welcome text accent
- Cards: White background + Green action buttons + Terracotta subtle highlights
- Dashboard: Cream background + Green progress bars + Terracotta greeting messages

### Typography

**Canonical Fonts (Web Applications):**
See "Canonical Design System" section above for THE standard:
- **Headings**: Libre Baskerville (serif)
- **Body**: Lato (sans-serif)

**Typography Principles:**
- Use clear, readable font sizes (minimum 16px for body text)
- Maintain good line height (1.5-1.7) for readability
- Use font weight to create hierarchy (600-700 for headings, 400-500 for body)
- Avoid decorative fonts; prioritize clarity and accessibility

**Canvas Fonts for Static Designs (Posters, PDFs):**
When creating posters, graphics, or PDF designs, use fonts from the `canvas-fonts/` directory.

**Primary Choice (matches web):**
- **LibreBaskerville** (Regular) - Canonical serif, matches web heading font

**Alternative Fonts (for variety in static designs only):**
- **Lora** (Regular, Bold, Italic, BoldItalic) - Warm, readable serif for elegant headings
- **WorkSans** (Regular, Bold, Italic, BoldItalic) - Friendly sans-serif, similar feel to Lato
- **InstrumentSans** (Regular, Bold, Italic, BoldItalic) - Clean, modern sans-serif
- **Outfit** (Regular, Bold) - Modern, approachable sans-serif
- **InstrumentSerif** (Regular, Italic) - Refined serif for sophisticated touches
- **CrimsonPro** (Regular, Bold, Italic) - Elegant serif for editorial content

**Font Pairing for Static Designs:**
- **Canonical**: LibreBaskerville (headings) + WorkSans (body) - Closest to web
- **Alternative Warm**: Lora (headings) + WorkSans (body)
- **Modern Editorial**: CrimsonPro (headings) + InstrumentSans (body)

### Design Aesthetic

**Visual Philosophy: "Nurturing Clarity"**

Houm's design aesthetic combines the professionalism of healthcare with the warmth of home care. The philosophy emphasizes:

- **Natural Forms**: Organic shapes, gentle curves, breathing room
- **Calm Palette**: Green-centered color harmony evoking growth and healing
- **Clear Communication**: Strong information hierarchy, readable typography
- **Warm Professionalism**: Trustworthy yet approachable visual language
- **Purposeful Simplicity**: Every element serves a clear function
- **Accessible Design**: High contrast, clear labels, intuitive interactions

**Design Don'ts (Avoiding "AI Slop"):**
- ❌ Excessive centered layouts
- ❌ Purple gradients or neon colors
- ❌ Uniform rounded corners everywhere
- ❌ Inter font with no variation
- ❌ Generic stock imagery
- ❌ Overly complex animations
- ❌ Cluttered interfaces

**Design Do's:**
- ✅ Asymmetric, intentional layouts
- ✅ Green-based natural color palette
- ✅ Varied border radius (subtle where needed)
- ✅ Typography hierarchy with different weights
- ✅ Authentic, relevant imagery
- ✅ Subtle, purposeful micro-interactions
- ✅ Clean, focused interfaces

## How to Use This Skill

The houmlike-design skill supports two primary workflows:

### 1. Building React-Based Web Artifacts

To create interactive web applications, dashboards, or complex interfaces:

**Step 1: Initialize Project**
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a React + TypeScript + Vite + Tailwind CSS + shadcn/ui project with Houm's design system pre-configured.

**Step 2: Develop the Artifact**
Edit the generated files to build the interface. Apply Houm's brand colors and design principles throughout. See the Tailwind configuration for Houm's color variables.

**Step 3: Bundle to Single HTML File**
```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact ready to share.

**Step 4: Share with User**
Present the bundled HTML file so it can be viewed as an artifact.

**Technical Stack:**
- React 18 + TypeScript + Vite
- Tailwind CSS 3.4.1 (with Houm color palette)
- shadcn/ui components
- Parcel for bundling

### 2. Creating Static Design Artifacts

To create visual designs, posters, graphics, or static materials:

**Step 1: Define Design Intent**
Understand the purpose, audience, and key message of the design.

**Step 2: Select Houm-Appropriate Fonts**
Use fonts from the `canvas-fonts/` directory. Recommended pairings:
- **Professional Warmth**: InstrumentSans + Lora
- **Modern Approachable**: Outfit + WorkSans
- **Classic Trust**: LibreBaskerville + WorkSans
- **Editorial Elegance**: CrimsonPro + InstrumentSerif

All fonts support Regular, Bold, and Italic variants for versatile typography.

**Step 3: Apply "Nurturing Clarity" Philosophy**
Use Houm's green palette, clean typography, and purposeful layouts. Emphasize:
- Visual hierarchy through color and scale
- Breathing room and whitespace
- Natural, organic visual elements
- Clear, accessible communication

**Step 4: Create Visual Output**
Generate PNG or PDF files using Houm's brand colors and design aesthetic. Ensure all designs:
- Use Houm's color palette (greens #4b7a4c through #e4ebe4, cream #f5efdf)
- Use fonts from `canvas-fonts/` directory for consistent branding
- Maintain high contrast for readability (WCAG AA)
- Reflect maternity care values (warm, professional, supportive)
- Avoid AI slop patterns (see Design Don'ts above)

## Design Components Library

When building React artifacts, leverage these shadcn/ui components styled with Houm's brand:

**Layout**: Card, Container, Separator
**Navigation**: Navigation Menu, Breadcrumb, Tabs
**Forms**: Input, Textarea, Select, Checkbox, Radio Group, Switch
**Feedback**: Alert, Toast, Dialog, Progress
**Data Display**: Table, Badge, Avatar

**Component Styling Guidelines:**
- Primary buttons: `bg-[#668e67]` with `hover:bg-[#4b7a4c]`
- Secondary buttons: `bg-[#98b298]` with `hover:bg-[#789b78]`
- Backgrounds: Use `bg-[#f5efdf]` or `bg-white`
- Borders: Use `border-[#c9d7c9]` or `border-[#a5bca5]`
- Text: Use `text-[#4b7a4c]` for headers, `text-gray-700` for body

## Accessibility Standards

All Houm designs must meet accessibility requirements:

- ✅ WCAG 2.1 AA compliance minimum
- ✅ Color contrast ratios of 4.5:1 for body text, 3:1 for large text
- ✅ Keyboard navigation support
- ✅ Screen reader compatibility
- ✅ Clear focus states
- ✅ Semantic HTML structure
- ✅ Alt text for all images
- ✅ Form labels and error messages

## Examples

**Example 1: Landing Page for Maternity Services**
Create a React-based landing page highlighting Houm's pregnancy care services. Use warm cream backgrounds (#f5efdf), dark green headers (#4b7a4c), and clear CTAs in forest green (#668e67). Include authentic imagery, clear service descriptions, and easy navigation.

**Example 2: Internal Dashboard for Healthcare Providers**
Build a React dashboard for Houm staff to track patient care. Use white/cream backgrounds, green accent colors for status indicators, and clear data visualization. Prioritize information hierarchy and quick access to key metrics.

**Example 3: Educational Poster about Informed Consent**
Design a static PDF poster using the "Nurturing Clarity" philosophy. Use InstrumentSans Bold for the main heading, Lora Regular for body text (from `canvas-fonts/`), large green typography in dark green (#4b7a4c), clear visual hierarchy, minimal text, and breathing room. Use cream backgrounds (#f5efdf) with subtle green accents. Focus on one key message with supporting visuals in Houm's color palette.

## Quality Standards

Every Houm design should:

1. **Reflect Brand Values** - Embody informed consent, evidence-based care, collaboration, and mindful intervention
2. **Use Brand Colors Consistently** - Apply Houm's green palette appropriately
3. **Maintain Professional Quality** - Appear polished, intentional, and expert-crafted
4. **Prioritize Accessibility** - Meet WCAG standards for inclusive design
5. **Avoid AI Slop** - Follow design best practices, not generic AI patterns
6. **Serve a Clear Purpose** - Every element should have a function
7. **Feel Warm Yet Professional** - Balance healthcare credibility with human warmth

## Resources

- **Canvas Fonts**: `canvas-fonts/` directory contains 7 curated font families (Lora, InstrumentSans, InstrumentSerif, WorkSans, Outfit, CrimsonPro, LibreBaskerville) for creating static design artifacts
- **Scripts**: `scripts/init-artifact.sh`, `scripts/bundle-artifact.sh` for React artifact workflow
- **Houm Website**: https://houmclinic.com/main/ for brand reference
- **shadcn/ui Docs**: https://ui.shadcn.com/docs/components for component reference
