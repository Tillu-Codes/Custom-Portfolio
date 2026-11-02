# Yadoji Sri Avegna — Developer & Designer Portfolio

A monochrome editorial portfolio for Yadoji Sri Avegna, built with semantic HTML, vanilla JavaScript, Tailwind CSS, and WebGL-driven motion.

## Highlights

- **Hero** — metallic editorial typography with an interactive portrait stage.
- **About** — scroll-expand media panel with a sticky, full-viewport reveal.
- **Experience** — horizontal timeline that translates vertical scroll into spatial progression.
- **Featured Projects** — OGL/WebGL liquid carousel with focus-on-click project modals.
- **Landing Pages** — draggable 3D drum wheel with indexed project cards.
- **Services** — accessible accordion with inquiry deep-links into the contact form.
- **Contact** — validated modal form delivered straight to email.

## Tech Stack

| Area | Tools |
|---|---|
| Structure | HTML5 |
| Styling | Vanilla CSS + Tailwind CSS (CDN) |
| Motion & Graphics | Vanilla JavaScript (ES Modules), OGL / WebGL, GSAP-style scroll effects |
| Typography | Plus Jakarta Sans (Google Fonts) |
| Contact | FormSubmit (AJAX delivery) |

## Project Structure

```bash
MyDesignPortfolio/
├── index.html                 # Single-page layout, styles and interactivity
├── FlexCarousel.css           # FlexCarousel layout and states
├── flex-carousel.js           # OGL/WebGL liquid project carousel
├── works-wheel.js             # 3D drum reel for landing pages
├── scroll-expand-media.js     # Scroll-driven media expansion engine
├── experience-section.js      # Horizontal spatial timeline engine
├── assets/                    # Hero, about imagery and string-tune module
├── Project Images/            # Featured project thumbnails
└── Landing Page Assets/       # Landing page thumbnails
```

## Run Locally

The site is fully static. Use any local HTTP server from the project root:

```bash
# Python
npm start

# or directly
python -m http.server 8080
```

Then open <http://localhost:8080>.

Alternatively use `npx serve .` or any other static server.

## Deploy

Deploy the repository root to Vercel, Netlify, GitHub Pages, or any static host. No build step is required.

## Connect

- **Instagram** — [@tillu_webs](https://www.instagram.com/tillu_webs)
- **X / Twitter** — [@sriavegna_17](https://x.com/sriavegna_17)
- **LinkedIn** — [Yadoji Sri Avegna](https://www.linkedin.com/in/yadoji-sri-avegna-0684a0381)
- **GitHub** — [Tillu-Codes](https://github.com/Tillu-Codes)
- **Email** — sriavegnayadoji@gmail.com

© Yadoji Sri Avegna. All rights reserved.
