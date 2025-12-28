# Fontend

## Gloabal architecture

```
frontend/
├── src/                 # Application source code
├── public/              # Static assets (webtab logo)
├── index.html           # Application entry HTML
├── package.json         # Dependencies and scripts
├── package-lock.json    # Dependency lock file
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
├── eslint.config.js     # Linting configuration
├── nginx.conf           # Nginx configuration for production
├── Dockerfile.dev       # Development container configuration
├── Dockerfile.prod      # Production container configuration
└── README.md            # Frontend documentation
```

## Source code

The `src/` folder contains the React application logic:

```
src/
├── components/          # Reusable UI building blocks
│   ├── Auth.jsx         # Login/Registration forms and logic
│   └── Dashboard.jsx    # The main application
├── api.js               # Centralized calls to the backend
├── App.css              # Global styles and Tailwind directives
├── App.jsx              # Main container handling routing and auth state
├── index.css            # Base styles
└── main.jsx             # The entry point that renders the React App
```
