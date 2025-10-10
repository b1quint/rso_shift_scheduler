# Frontend - React Application

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env if needed
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173/`

## Project Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── components/  # Reusable UI components
│   ├── features/    # Feature-based modules
│   │   ├── auth/    # Authentication
│   │   ├── shifts/  # Shift management
│   │   ├── staff/   # Staff management
│   │   └── schedule/# Schedule views
│   ├── services/    # API integration
│   ├── hooks/       # Custom React hooks
│   ├── utils/       # Helper functions
│   ├── App.jsx      # Main app component
│   └── main.jsx     # Entry point
├── package.json
└── vite.config.js
```

## Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

## Technology Choices

- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **CSS**: You can add Tailwind CSS or Material-UI later
