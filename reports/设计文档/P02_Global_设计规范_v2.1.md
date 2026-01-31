# Visual Design Specification v2.1: "The Athenaeum" (Paper Mode)

## 1. Design Philosophy
**"Digital Ink on Archival Paper"**
The interface should feel like a premium printed academic journal or a high-end e-reader. It prioritizes long-form reading comfort, typographic hierarchy, and intellectual focus over "tech" aesthetics.

## 2. Color System (Warm Low-Contrast)

| Token | Hex Value | Tailwind Class | Usage |
| :--- | :--- | :--- | :--- |
| **Background** | `#F9F8F6` | `bg-[#F9F8F6]` | Main app background (Warm Paper) |
| **Surface** | `#FFFFFF` | `bg-white` | Cards (Sidebar, Inspector) - *Subtle differentiation* |
| **Ink Primary** | `#27272A` | `text-zinc-800` | Main distinct text (Soft Black) |
| **Ink Secondary** | `#52525B` | `text-zinc-600` | Metadata, UI Labels |
| **Ink Tertiary** | `#A1A1AA` | `text-zinc-400` | Placeholders, inactive icons |
| **Accent** | `#E4E4E7` | `border-zinc-200` | Borders, Separators (Crisp, light) |
| **Highlight** | `#F4F4F5` | `bg-zinc-100` | Hover states, active items |

**Critique & Adjustment:**
*   *Avoid pure #000000.* Use `#18181B` (Zinc-950) or `#27272A` (Zinc-800) for "Ink" to reduce eye strain against the light background.
*   *Sidebar Separation:* Instead of lines, use a subtle background shift. Sidebar: `#F4F4F5` (Zinc-100), Editor: `#FEFCF8` (Warm White).

## 3. Typography (The Golden Pair)

### **UI Font (Navigation, Sidebar, Tools)**
*   **Family:** `Geist Sans` (Existing), `Inter`, or `SF Pro`.
*   **Role:** Functional, legible at small sizes (11px-13px).
*   **Weight:** Medium (500) for labels, Regular (400) for data.

### **Content Font (The 'Ink')**
*   **Family:** **Serif** is non-negotiable for this style.
*   **Recommendation:** `Newsreader` (Google Fonts) or `Merriweather`.
*   **Role:** The main editor canvas.
*   **Line Height:** `leading-relaxed` (1.75).
*   **Tracking:** `tracking-tight` (-0.01em) for headlines.

## 4. Layout & Spacing (Breathability)

*   **Margins:** Increase editor horizontal padding. `max-w-3xl` centered.
*   **Density:**
    *   *Sidebar:* Compact (High density) for efficiency.
    *   *Editor:* Loose (Low density) for reading.
*   **Corner Radius:** `rounded-sm` (2px-4px). "Paper" doesn't have large rounded corners. Avoid `rounded-xl`.

## 5. Refinements Checklist (User Requested)
> "Scrutinize fonts, spacing, colors..."

1.  [ ] **Action:** Add `Newsreader` font to `layout.tsx`.
2.  [ ] **Action:** Calibrate `globals.css` to use the `#F9F8F6` background.
3.  [ ] **Action:** In `WritingCanvas`, increase `px-8` to `px-12` or `px-16` for that "Thesis" feel.
4.  [ ] **Action:** Ensure Sidebar items have distinct "Active" state (e.g., a simple left vertical bar or bold text) without glowing.
