import json
import os

# Create comprehensive project structure
project_structure = {
    "figma-clone": {
        "README.md": "# DesignStudio - Mobile-First Design Collaboration Platform\n\nA production-ready Figma-like design and collaboration application built with React Native and modern web technologies.",
        "packages": {
            "mobile": {
                "package.json": {
                    "name": "@designstudio/mobile",
                    "version": "1.0.0",
                    "description": "React Native mobile application",
                    "main": "index.js",
                    "scripts": {
                        "android": "react-native run-android",
                        "ios": "react-native run-ios",
                        "start": "react-native start",
                        "test": "jest",
                        "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
                        "type-check": "tsc --noEmit"
                    },
                    "dependencies": {
                        "react": "18.2.0",
                        "react-native": "0.73.6",
                        "react-native-svg": "^15.1.0",
                        "react-native-vector-icons": "^10.0.3",
                        "react-native-gesture-handler": "^2.14.0",
                        "react-native-reanimated": "^3.6.2",
                        "react-native-webrtc": "^118.0.0",
                        "@react-native-async-storage/async-storage": "^1.21.0",
                        "@react-navigation/native": "^6.1.9",
                        "@react-navigation/stack": "^6.3.20",
                        "socket.io-client": "^4.7.4",
                        "@supabase/supabase-js": "^2.39.0",
                        "react-native-url-polyfill": "^2.0.0"
                    },
                    "devDependencies": {
                        "@babel/core": "^7.20.0",
                        "@babel/preset-env": "^7.20.0",
                        "@babel/runtime": "^7.20.0",
                        "@react-native/eslint-config": "^0.73.1",
                        "@react-native/metro-config": "^0.73.2",
                        "@react-native/typescript-config": "^0.73.1",
                        "@types/react": "^18.0.24",
                        "@types/react-test-renderer": "^18.0.0",
                        "babel-jest": "^29.2.1",
                        "eslint": "^8.19.0",
                        "jest": "^29.2.1",
                        "metro-react-native-babel-preset": "0.73.5",
                        "prettier": "^2.4.1",
                        "react-test-renderer": "18.2.0",
                        "typescript": "4.8.4"
                    }
                },
                "tsconfig.json": {
                    "extends": "@react-native/typescript-config/tsconfig.json",
                    "compilerOptions": {
                        "strict": True,
                        "noImplicitAny": True,
                        "strictNullChecks": True,
                        "strictFunctionTypes": True,
                        "noImplicitReturns": True,
                        "noFallthroughCasesInSwitch": True,
                        "moduleResolution": "node",
                        "allowSyntheticDefaultImports": True,
                        "esModuleInterop": True,
                        "skipLibCheck": True,
                        "resolveJsonModule": True,
                        "baseUrl": "./src",
                        "paths": {
                            "@/*": ["*"],
                            "@components/*": ["components/*"],
                            "@screens/*": ["screens/*"],
                            "@services/*": ["services/*"],
                            "@utils/*": ["utils/*"],
                            "@types/*": ["types/*"]
                        }
                    },
                    "include": ["src/**/*", "index.js"],
                    "exclude": ["node_modules", "build", "dist"]
                },
                "src": {
                    "App.tsx": "// Main React Native App Component\nimport React from 'react';\nimport { NavigationContainer } from '@react-navigation/native';\nimport { createStackNavigator } from '@react-navigation/stack';\nimport { DesignCanvas } from './screens/DesignCanvas';\nimport { AuthProvider } from './providers/AuthProvider';\nimport { CollaborationProvider } from './providers/CollaborationProvider';\n\nconst Stack = createStackNavigator();\n\nexport default function App(): React.JSX.Element {\n  return (\n    <AuthProvider>\n      <CollaborationProvider>\n        <NavigationContainer>\n          <Stack.Navigator screenOptions={{ headerShown: false }}>\n            <Stack.Screen name=\"Canvas\" component={DesignCanvas} />\n          </Stack.Navigator>\n        </NavigationContainer>\n      </CollaborationProvider>\n    </AuthProvider>\n  );\n}",
                    "components": {
                        "ToolPalette.tsx": "// Tool palette component",
                        "Canvas": {
                            "CanvasView.tsx": "// Main canvas rendering component",
                            "VectorRenderer.tsx": "// SVG vector graphics renderer", 
                            "ObjectManager.tsx": "// Manages canvas objects"
                        },
                        "Panels": {
                            "PropertyPanel.tsx": "// Object property editor",
                            "LayerPanel.tsx": "// Layer management",
                            "ColorPicker.tsx": "// Color selection component"
                        },
                        "Collaboration": {
                            "LiveCursors.tsx": "// Real-time cursor display",
                            "UserList.tsx": "// Online users component",
                            "Comments.tsx": "// Comment system"
                        }
                    },
                    "screens": {
                        "DesignCanvas.tsx": "// Main design interface screen",
                        "ProjectsScreen.tsx": "// Project management screen",
                        "ExportScreen.tsx": "// Export options screen"
                    },
                    "services": {
                        "CanvasService.ts": "// Canvas operations service",
                        "CollaborationService.ts": "// Real-time collaboration",
                        "VectorEngine.ts": "// Vector graphics engine",
                        "ExportService.ts": "// Export functionality"
                    },
                    "types": {
                        "Canvas.ts": "// Canvas-related types",
                        "Collaboration.ts": "// Collaboration types",
                        "Vector.ts": "// Vector graphics types"
                    },
                    "utils": {
                        "Vector.ts": "// Vector math utilities",
                        "Transform.ts": "// Transformation utilities",
                        "Performance.ts": "// Performance optimization"
                    }
                }
            },
            "web": {
                "package.json": {
                    "name": "@designstudio/web",
                    "version": "1.0.0",
                    "description": "Progressive Web App for desktop collaboration",
                    "scripts": {
                        "dev": "vite",
                        "build": "tsc && vite build",
                        "preview": "vite preview",
                        "test": "vitest",
                        "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                        "type-check": "tsc --noEmit"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "fabric": "^5.3.0",
                        "socket.io-client": "^4.7.4",
                        "@supabase/supabase-js": "^2.39.0",
                        "framer-motion": "^10.16.16",
                        "zustand": "^4.4.7",
                        "react-hotkeys-hook": "^4.4.1",
                        "react-color": "^2.19.3",
                        "file-saver": "^2.0.5"
                    },
                    "devDependencies": {
                        "@types/react": "^18.2.43",
                        "@types/react-dom": "^18.2.17",
                        "@typescript-eslint/eslint-plugin": "^6.14.0",
                        "@typescript-eslint/parser": "^6.14.0",
                        "@vitejs/plugin-react": "^4.2.1",
                        "eslint": "^8.55.0",
                        "eslint-plugin-react-hooks": "^4.6.0",
                        "eslint-plugin-react-refresh": "^0.4.5",
                        "typescript": "^5.2.2",
                        "vite": "^5.0.8",
                        "vite-plugin-pwa": "^0.17.4",
                        "vitest": "^1.0.4"
                    }
                },
                "vite.config.ts": "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\nimport { VitePWA } from 'vite-plugin-pwa';\n\nexport default defineConfig({\n  plugins: [\n    react(),\n    VitePWA({\n      registerType: 'autoUpdate',\n      workbox: {\n        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],\n        runtimeCaching: [\n          {\n            urlPattern: /^https:\\/\\/api\\./,\n            handler: 'NetworkFirst',\n            options: {\n              cacheName: 'api-cache',\n              cacheableResponse: {\n                statuses: [0, 200]\n              }\n            }\n          }\n        ]\n      },\n      manifest: {\n        name: 'DesignStudio',\n        short_name: 'DesignStudio',\n        description: 'Mobile-First Design Collaboration Platform',\n        theme_color: '#21808d',\n        background_color: '#fcfcf9',\n        display: 'standalone',\n        icons: [\n          {\n            src: 'pwa-192x192.png',\n            sizes: '192x192',\n            type: 'image/png'\n          },\n          {\n            src: 'pwa-512x512.png', \n            sizes: '512x512',\n            type: 'image/png'\n          }\n        ]\n      }\n    })\n  ],\n  resolve: {\n    alias: {\n      '@': '/src'\n    }\n  }\n});",
                "src": {
                    "main.tsx": "// PWA entry point",
                    "components": {
                        "DesignCanvas.tsx": "// Desktop canvas component",
                        "ToolbarDesktop.tsx": "// Desktop toolbar"
                    }
                }
            },
            "backend": {
                "package.json": {
                    "name": "@designstudio/backend",
                    "version": "1.0.0",
                    "description": "Node.js backend with real-time collaboration",
                    "main": "dist/index.js",
                    "scripts": {
                        "dev": "tsx watch src/index.ts",
                        "build": "tsc",
                        "start": "node dist/index.js",
                        "test": "jest",
                        "lint": "eslint src --ext .ts",
                        "prisma:generate": "prisma generate",
                        "prisma:migrate": "prisma migrate dev",
                        "prisma:push": "prisma db push",
                        "prisma:studio": "prisma studio"
                    },
                    "dependencies": {
                        "express": "^4.18.2",
                        "socket.io": "^4.7.4",
                        "cors": "^2.8.5",
                        "helmet": "^7.1.0",
                        "compression": "^1.7.4",
                        "express-rate-limit": "^7.1.5",
                        "@prisma/client": "^5.7.1",
                        "prisma": "^5.7.1",
                        "bcryptjs": "^2.4.3",
                        "jsonwebtoken": "^9.0.2",
                        "zod": "^3.22.4",
                        "winston": "^3.11.0",
                        "redis": "^4.6.10",
                        "dotenv": "^16.3.1",
                        "multer": "^1.4.5-lts.1",
                        "sharp": "^0.33.1"
                    },
                    "devDependencies": {
                        "@types/node": "^20.10.4",
                        "@types/express": "^4.17.21",
                        "@types/cors": "^2.8.17",
                        "@types/compression": "^1.7.5",
                        "@types/bcryptjs": "^2.4.6",
                        "@types/jsonwebtoken": "^9.0.5",
                        "@types/multer": "^1.4.11",
                        "typescript": "^5.3.3",
                        "tsx": "^4.6.2",
                        "jest": "^29.7.0",
                        "@types/jest": "^29.5.8",
                        "eslint": "^8.55.0",
                        "@typescript-eslint/eslint-plugin": "^6.14.0",
                        "@typescript-eslint/parser": "^6.14.0"
                    }
                },
                "tsconfig.json": {
                    "compilerOptions": {
                        "target": "ES2022",
                        "module": "commonjs",
                        "lib": ["ES2022"],
                        "outDir": "./dist",
                        "rootDir": "./src",
                        "strict": True,
                        "esModuleInterop": True,
                        "skipLibCheck": True,
                        "forceConsistentCasingInFileNames": True,
                        "resolveJsonModule": True,
                        "declaration": True,
                        "declarationMap": True,
                        "sourceMap": True,
                        "removeComments": True,
                        "noImplicitReturns": True,
                        "noFallthroughCasesInSwitch": True,
                        "moduleResolution": "node",
                        "baseUrl": "./src",
                        "paths": {
                            "@/*": ["*"],
                            "@controllers/*": ["controllers/*"],
                            "@services/*": ["services/*"],
                            "@models/*": ["models/*"],
                            "@utils/*": ["utils/*"],
                            "@types/*": ["types/*"]
                        }
                    },
                    "include": ["src/**/*"],
                    "exclude": ["node_modules", "dist", "**/*.test.ts"]
                },
                "prisma": {
                    "schema.prisma": """
// Prisma schema for DesignStudio
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mongodb"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  email     String   @unique
  name      String
  avatar    String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  projects     Project[]
  comments     Comment[]
  sessions     Session[]
  collaborations Collaboration[]

  @@map("users")
}

model Project {
  id          String   @id @default(auto()) @map("_id") @db.ObjectId
  name        String
  description String?
  thumbnail   String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  ownerId     String   @db.ObjectId

  // Relations
  owner         User            @relation(fields: [ownerId], references: [id])
  artboards     Artboard[]
  collaborations Collaboration[]
  comments      Comment[]
  versions      Version[]

  @@map("projects")
}

model Artboard {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  name      String
  width     Int
  height    Int
  x         Float    @default(0)
  y         Float    @default(0)
  objects   Json     @default("[]")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  projectId String   @db.ObjectId

  // Relations
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@map("artboards")
}

model Collaboration {
  id          String   @id @default(auto()) @map("_id") @db.ObjectId
  role        String   // "owner", "editor", "viewer"
  permissions Json     @default("{}")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  userId      String   @db.ObjectId
  projectId   String   @db.ObjectId

  // Relations
  user    User    @relation(fields: [userId], references: [id])
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@unique([userId, projectId])
  @@map("collaborations")
}

model Comment {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  content   String
  x         Float
  y         Float
  resolved  Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  authorId  String   @db.ObjectId
  projectId String   @db.ObjectId

  // Relations
  author  User    @relation(fields: [authorId], references: [id])
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)
  replies Reply[]

  @@map("comments")
}

model Reply {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  content   String
  createdAt DateTime @default(now())
  commentId String   @db.ObjectId
  authorId  String   @db.ObjectId

  // Relations
  comment Comment @relation(fields: [commentId], references: [id], onDelete: Cascade)

  @@map("replies")
}

model Session {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  cursor    Json?
  selection Json?
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  userId    String   @db.ObjectId
  projectId String   @db.ObjectId

  // Relations
  user User @relation(fields: [userId], references: [id])

  @@map("sessions")
}

model Version {
  id          String   @id @default(auto()) @map("_id") @db.ObjectId
  name        String
  description String?
  snapshot    Json
  createdAt   DateTime @default(now())
  projectId   String   @db.ObjectId

  // Relations
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@map("versions")
}
"""
                },
                "src": {
                    "index.ts": "// Main server entry point",
                    "controllers": {
                        "AuthController.ts": "// Authentication endpoints",
                        "ProjectController.ts": "// Project management",
                        "CollaborationController.ts": "// Real-time collaboration"
                    },
                    "services": {
                        "SocketService.ts": "// WebSocket management",
                        "OperationalTransform.ts": "// OT implementation",
                        "CacheService.ts": "// Redis caching"
                    },
                    "middleware": {
                        "auth.ts": "// Authentication middleware",
                        "validation.ts": "// Request validation"
                    },
                    "types": {
                        "api.ts": "// API type definitions",
                        "socket.ts": "// Socket event types"
                    }
                }
            },
            "shared": {
                "package.json": {
                    "name": "@designstudio/shared",
                    "version": "1.0.0",
                    "description": "Shared types and utilities",
                    "main": "dist/index.js",
                    "types": "dist/index.d.ts",
                    "scripts": {
                        "build": "tsc",
                        "dev": "tsc --watch",
                        "test": "jest"
                    },
                    "dependencies": {
                        "zod": "^3.22.4"
                    },
                    "devDependencies": {
                        "typescript": "^5.3.3",
                        "@types/node": "^20.10.4",
                        "jest": "^29.7.0",
                        "@types/jest": "^29.5.8"
                    }
                },
                "src": {
                    "types": {
                        "Canvas.ts": "// Shared canvas types",
                        "User.ts": "// User-related types",
                        "Project.ts": "// Project structure types"
                    },
                    "utils": {
                        "Vector.ts": "// Vector math utilities",
                        "Validation.ts": "// Shared validation schemas"
                    }
                }
            }
        },
        "docker-compose.yml": """version: '3.8'

services:
  # MongoDB Database
  mongodb:
    image: mongo:7
    container_name: designstudio-mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
      MONGO_INITDB_DATABASE: designstudio
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./docker/mongodb/init:/docker-entrypoint-initdb.d
    networks:
      - designstudio-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: designstudio-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - designstudio-network

  # Backend API
  backend:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile
    container_name: designstudio-backend
    restart: unless-stopped
    environment:
      NODE_ENV: development
      PORT: 3000
      DATABASE_URL: mongodb://admin:password@mongodb:27017/designstudio?authSource=admin
      REDIS_URL: redis://redis:6379
      JWT_SECRET: your-jwt-secret
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY}
    ports:
      - "3000:3000"
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./packages/backend:/app
      - /app/node_modules
    networks:
      - designstudio-network

  # Web PWA
  web:
    build:
      context: ./packages/web
      dockerfile: Dockerfile
    container_name: designstudio-web
    restart: unless-stopped
    environment:
      VITE_API_URL: http://localhost:3000
      VITE_SUPABASE_URL: ${SUPABASE_URL}
      VITE_SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY}
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./packages/web:/app
      - /app/node_modules
    networks:
      - designstudio-network

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    container_name: designstudio-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - web
    networks:
      - designstudio-network

volumes:
  mongodb_data:
  redis_data:

networks:
  designstudio-network:
    driver: bridge
""",
        ".github": {
            "workflows": {
                "ci-cd.yml": """name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
        
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'yarn'
          
      - name: Install dependencies
        run: yarn install --frozen-lockfile
        
      - name: Type checking
        run: yarn type-check
        
      - name: Linting
        run: yarn lint
        
      - name: Unit tests
        run: yarn test
        
      - name: Build packages
        run: yarn build

  build-mobile-android:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'yarn'
          
      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          
      - name: Setup Android SDK
        uses: android-actions/setup-android@v3
        
      - name: Install dependencies
        run: |
          cd packages/mobile
          yarn install
          
      - name: Build Android
        run: |
          cd packages/mobile
          cd android
          ./gradlew assembleRelease
          
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: android-apk
          path: packages/mobile/android/app/build/outputs/apk/release/

  build-mobile-ios:
    needs: test
    runs-on: macos-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'yarn'
          
      - name: Install dependencies
        run: |
          cd packages/mobile
          yarn install
          cd ios
          pod install
          
      - name: Build iOS
        run: |
          cd packages/mobile
          npx react-native run-ios --configuration Release

  deploy-staging:
    needs: [test, build-mobile-android]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to staging
        env:
          DEPLOY_HOST: ${{ secrets.STAGING_HOST }}
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          echo "Deploying to staging environment"
          # Add deployment scripts here

  deploy-production:
    needs: [test, build-mobile-android, build-mobile-ios]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        env:
          DEPLOY_HOST: ${{ secrets.PRODUCTION_HOST }}
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          echo "Deploying to production environment"
          # Add deployment scripts here
""",
                "mobile-release.yml": """name: Mobile Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          
      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          
      - name: Decode Keystore
        env:
          ENCODED_STRING: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo $ENCODED_STRING | base64 -di > packages/mobile/android/app/my-upload-key.keystore
          
      - name: Build Android App Bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: |
          cd packages/mobile
          yarn install
          cd android
          ./gradlew bundleRelease
          
      - name: Upload to Play Console
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.designstudio.app
          releaseFiles: packages/mobile/android/app/build/outputs/bundle/release/app-release.aab
          track: production

  release-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          
      - name: Install dependencies
        run: |
          cd packages/mobile
          yarn install
          cd ios
          pod install
          
      - name: Build and upload to TestFlight
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          FASTLANE_PASSWORD: ${{ secrets.FASTLANE_PASSWORD }}
        run: |
          cd packages/mobile/ios
          fastlane release
"""
            }
        }
    }
}

# Save project structure to JSON
with open('project_structure.json', 'w') as f:
    json.dump(project_structure, f, indent=2)

print("Project structure created successfully!")
print("\nMain directories:")
for key in project_structure["figma-clone"]["packages"].keys():
    print(f"- packages/{key}")