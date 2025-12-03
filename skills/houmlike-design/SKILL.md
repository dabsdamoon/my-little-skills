---
name: houmlike-design
description: Create web UI, interfaces, landing pages, and design artifacts for Houm, a maternity care service provider. This skill should be used when designing or building any visual or interactive elements for Houm's digital presence, applying Houm's brand identity, values, and design philosophy.
license: Complete terms in LICENSE.txt
---

# Houmlike Design

To create designs and interfaces for Houm, use this skill. Houm is a maternity care service provider committed to transforming the maternity care experience through informed consent, evidence-based care, companion support, and mindful intervention.

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

**Primary Palette (Greens):**
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

**Accent Colors:**

- Warm Cream: `#f5efdf` - Primary background, warm accents
- Pure White: `#ffffff` - Clean backgrounds
- Soft White: `#f6f8f6` - Alternative light backgrounds

**Usage Guidelines:**
- Use darker greens (#4b7a4c, #668e67) for text and primary actions
- Use mid-range greens (#789b78, #8aa88a, #81a282) for interactive elements
- Use lighter greens (#98b298, #a5bca5, #c9d7c9, #e4ebe4) for backgrounds and subtle divisions
- Use cream (#f5efdf) as a warm, inviting background alternative to white
- Maintain high contrast for accessibility (WCAG AA minimum)

### Typography

**Font Recommendations:**
While Houm's website uses system fonts, for artifacts use these professional, healthcare-appropriate fonts:

- **Headings**: InstrumentSans, WorkSans, or Outfit (clean, modern sans-serif)
- **Body Text**: WorkSans, InstrumentSans, or system-ui (readable sans-serif)
- **Serif Options**: Lora, CrimsonPro, InstrumentSerif, LibreBaskerville (for warmth in editorial content)

**Typography Principles:**
- Use clear, readable font sizes (minimum 16px for body text)
- Maintain good line height (1.5-1.7) for readability
- Use font weight to create hierarchy (600-700 for headings, 400-500 for body)
- Avoid decorative fonts; prioritize clarity and accessibility

**Canvas Fonts for Static Designs:**
When creating posters, graphics, or PDF designs, use fonts from the `canvas-fonts/` directory:

**Recommended for Houm:**
- **Lora** (Regular, Bold, Italic, BoldItalic) - Warm, readable serif perfect for maternity care content. Use for body text or elegant headings.
- **InstrumentSans** (Regular, Bold, Italic, BoldItalic) - Clean, modern sans-serif with professional warmth. Ideal for headings and UI text.
- **WorkSans** (Regular, Bold, Italic, BoldItalic) - Friendly, professional sans-serif. Great for body text and accessible designs.
- **Outfit** (Regular, Bold) - Modern, approachable sans-serif. Use for contemporary headings.
- **InstrumentSerif** (Regular, Italic) - Refined serif for sophisticated touches.
- **CrimsonPro** (Regular, Bold, Italic) - Elegant serif for editorial content.
- **LibreBaskerville** (Regular) - Classic, trustworthy serif for traditional healthcare materials.

**Font Pairing Suggestions:**
- **Professional Warmth**: InstrumentSans (headings) + Lora (body)
- **Modern Approachable**: Outfit (headings) + WorkSans (body)
- **Classic Trust**: LibreBaskerville (headings) + WorkSans (body)
- **Editorial Elegance**: CrimsonPro (headings) + InstrumentSerif (body)

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
