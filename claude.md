# Plan de Implementación: Plataforma de Exámenes Simuladores EXANI-II

## Resumen Ejecutivo

Crear una plataforma web completa para simulacros del examen EXANI-II que permita:
- Subir exámenes mediante archivos JSON
- Realizar simulacros temporizados
- Ver resultados y retroalimentación detallada
- Gestionar exámenes desde panel admin
- Historial de intentos del usuario

**Stack:** Next.js 15 + TypeScript + Prisma + PostgreSQL + Tailwind CSS + Vercel

---

## Estructura del Proyecto

```
exani-simulator/
├── app/
│   ├── layout.tsx                          # Layout principal
│   ├── page.tsx                            # Home: lista de exámenes
│   ├── globals.css                         # Estilos globales Tailwind
│   ├── exam/
│   │   ├── [id]/page.tsx                   # Simulacro interactivo
│   │   └── results/[examId]/page.tsx       # Resultados detallados
│   ├── dashboard/
│   │   └── page.tsx                        # Historial de intentos
│   ├── admin/
│   │   ├── page.tsx                        # Admin dashboard
│   │   ├── upload/page.tsx                 # Subir JSON
│   │   └── exams/[id]/page.tsx            # Editar examen
│   └── api/
│       ├── exams/
│       │   ├── route.ts                    # GET: lista, POST: crear
│       │   └── [id]/route.ts               # GET: detalle, PUT: actualizar, DELETE
│       ├── questions/
│       │   ├── route.ts                    # POST: crear pregunta
│       │   └── [id]/route.ts               # PUT: actualizar, DELETE
│       ├── upload/
│       │   └── route.ts                    # POST: subir JSON
│       ├── attempts/
│       │   ├── route.ts                    # GET: historial, POST: guardar
│       │   └── [id]/route.ts               # GET: detalle de intento
│       └── submit/
│           └── route.ts                    # POST: enviar respuestas
├── components/
│   ├── ui/                                 # Componentes base
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   ├── ExamCard.tsx                        # Card de examen en home
│   ├── ExamPlayer.tsx                      # Motor del simulacro
│   ├── QuestionDisplay.tsx                 # Display de pregunta individual
│   ├── Timer.tsx                           # Temporizador
│   ├── ProgressBar.tsx                     # Barra de progreso
│   ├── ResultsDisplay.tsx                  # Visualización de resultados
│   ├── Navigation.tsx                      # Navegación de preguntas
│   ├── AdminExamList.tsx                   # Lista en admin
│   ├── AdminQuestionForm.tsx               # Form para editar preguntas
│   └── JsonUploadForm.tsx                  # Form para subir JSON
├── lib/
│   ├── db.ts                               # Cliente Prisma
│   ├── types.ts                            # Interfaces TypeScript
│   ├── utils.ts                            # Helpers generales
│   ├── exam-utils.ts                       # Lógica de calificación
│   └── json-validator.ts                   # Validación de JSONs
├── prisma/
│   ├── schema.prisma                       # Esquema de base de datos
│   └── seed.ts                             # Datos iniciales (opcional)
├── public/
│   └── placeholder.png                     # Placeholder para imágenes
├── .env.local                              # Variables de entorno
├── .env.example                            # Ejemplo de variables
├── .gitignore
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## Esquema de Base de Datos (Prisma)

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Exam {
  id          String      @id @default(cuid())
  title       String      // "Pensamiento Matemático"
  subject     String      // "matematica", "lengua", "general"
  duration    Int         // Minutos
  description String?
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
  questions   Question[]
  attempts    Attempt[]

  @@index([subject])
}

model Question {
  id            String   @id @default(cuid())
  examId        String
  exam          Exam     @relation(fields: [examId], references: [id], onDelete: Cascade)
  number        Int      // Orden en el examen
  text          String   @db.Text
  image         String?  // URL o null
  options       String[] // ["Opción 1", "Opción 2", "Opción 3", "Opción 4"]
  correctAnswer String   // "Opción 2" (el texto exacto)
  explanation   String   @db.Text
  difficulty    String   @default("medium") // "easy", "medium", "hard"
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  @@index([examId])
  @@unique([examId, number])
}

model Attempt {
  id          String   @id @default(cuid())
  examId      String
  exam        Exam     @relation(fields: [examId], references: [id])
  userId      String   // UUID generado en frontend (localStorage)
  answers     Json     // {"1": "Opción A", "2": "Opción B", ...}
  score       Float    // Porcentaje (0-100)
  correct     Int      // Número de correctas
  total       Int      // Total de preguntas
  timeSpent   Int?     // Segundos gastados
  completedAt DateTime @default(now())

  @@index([userId])
  @@index([examId])
}
```

---

## Formato JSON para Upload

```json
{
  "title": "Pensamiento Matemático EXANI-II",
  "subject": "matematica",
  "duration": 90,
  "description": "Simulacro de 40 preguntas de matemáticas",
  "questions": [
    {
      "number": 1,
      "text": "¿Cuál es el resultado de resolver la ecuación 2x + 5 = 13?",
      "image": null,
      "options": [
        "x = 3",
        "x = 4",
        "x = 5",
        "x = 6"
      ],
      "correctAnswer": "x = 4",
      "explanation": "Despejando: 2x = 13 - 5 = 8, entonces x = 8/2 = 4",
      "difficulty": "easy"
    },
    {
      "number": 2,
      "text": "¿Cuál es el área de un círculo con radio 5 cm?",
      "image": "https://example.com/circulo.png",
      "options": [
        "25π cm²",
        "10π cm²",
        "15π cm²",
        "20π cm²"
      ],
      "correctAnswer": "25π cm²",
      "explanation": "A = πr² = π(5)² = 25π cm²",
      "difficulty": "medium"
    }
  ]
}
```

---

## Plan de Implementación Paso a Paso

### Fase 1: Setup Inicial del Proyecto

**Paso 1.1:** Inicializar Next.js con TypeScript
```bash
npx create-next-app@latest exani-simulator --typescript --tailwind --app --eslint
cd exani-simulator
```

**Paso 1.2:** Instalar dependencias adicionales
```bash
npm install @prisma/client
npm install -D prisma
npm install zod # Para validación
npm install date-fns # Para manejo de fechas
npm install react-hot-toast # Para notificaciones
```

**Paso 1.3:** Inicializar Prisma
```bash
npx prisma init
```

**Paso 1.4:** Configurar variables de entorno
Crear `.env.local`:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/exani_db?schema=public"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

Crear `.env.example`:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/exani_db?schema=public"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

---

### Fase 2: Base de Datos

**Paso 2.1:** Crear el schema de Prisma (schema.prisma)
- Copiar el esquema definido arriba

**Paso 2.2:** Ejecutar migración
```bash
npx prisma migrate dev --name init
```

**Paso 2.3:** Crear cliente de Prisma
Archivo: `lib/db.ts`
```typescript
import { PrismaClient } from '@prisma/client'

const globalForPrisma = global as unknown as { prisma: PrismaClient }

export const prisma = globalForPrisma.prisma || new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

---

### Fase 3: TypeScript Types & Utils

**Paso 3.1:** Crear types (lib/types.ts)
```typescript
export interface ExamJSON {
  title: string
  subject: string
  duration: number
  description?: string
  questions: QuestionJSON[]
}

export interface QuestionJSON {
  number: number
  text: string
  image?: string | null
  options: string[]
  correctAnswer: string
  explanation: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface UserAnswer {
  questionNumber: number
  answer: string
  isCorrect: boolean
}

export interface ExamResult {
  score: number
  correct: number
  total: number
  answers: UserAnswer[]
  timeSpent: number
}
```

**Paso 3.2:** Crear validador JSON (lib/json-validator.ts)
- Usar Zod para validar estructura del JSON subido

**Paso 3.3:** Crear utils de examen (lib/exam-utils.ts)
- Función para calcular puntaje
- Función para generar examen general (combinando varios temas)
- Función para shuffle opciones (opcional)

---

### Fase 4: API Routes

**Paso 4.1:** API de Exámenes
- `app/api/exams/route.ts`: GET (listar), POST (crear)
- `app/api/exams/[id]/route.ts`: GET (detalle), PUT (actualizar), DELETE

**Paso 4.2:** API de Upload JSON
- `app/api/upload/route.ts`: Validar JSON + crear examen con preguntas

**Paso 4.3:** API de Questions
- `app/api/questions/route.ts`: POST (crear pregunta individual)
- `app/api/questions/[id]/route.ts`: PUT (actualizar), DELETE

**Paso 4.4:** API de Attempts
- `app/api/attempts/route.ts`: GET (historial por userId), POST (crear)
- `app/api/attempts/[id]/route.ts`: GET (detalle de intento)

**Paso 4.5:** API de Submit
- `app/api/submit/route.ts`: POST (recibir respuestas, calcular score, guardar attempt)

---

### Fase 5: Componentes UI Base

**Paso 5.1:** Crear componentes base en `components/ui/`
- Button.tsx
- Card.tsx
- Input.tsx
- Modal.tsx (para confirmaciones)

**Paso 5.2:** Configurar Tailwind
- Agregar colores personalizados al theme
- Configurar tipografías

---

### Fase 6: Componentes de Examen

**Paso 6.1:** ExamCard.tsx
- Muestra info del examen en home
- Botón "Comenzar examen"

**Paso 6.2:** Timer.tsx
- Cuenta regresiva
- Alerta cuando quedan 5 minutos
- Auto-submit cuando termina el tiempo

**Paso 6.3:** QuestionDisplay.tsx
- Muestra pregunta con número
- Opciones como radio buttons
- Soporte para imagen (si existe)
- Marca la opción seleccionada

**Paso 6.4:** Navigation.tsx
- Grid de números de pregunta
- Indica: respondida, actual, sin responder
- Click para saltar a pregunta

**Paso 6.5:** ProgressBar.tsx
- Barra visual de progreso
- Muestra "X de Y preguntas respondidas"

**Paso 6.6:** ExamPlayer.tsx
- Motor principal del examen
- Maneja estado de respuestas
- Integra Timer, QuestionDisplay, Navigation
- Botones: Anterior, Siguiente, Finalizar
- Modal de confirmación al finalizar

**Paso 6.7:** ResultsDisplay.tsx
- Muestra score final
- Desglose por pregunta (correcta/incorrecta)
- Muestra explicaciones
- Gráfica de desempeño (opcional)

---

### Fase 7: Páginas Frontend

**Paso 7.1:** Home (app/page.tsx)
- Lista de exámenes disponibles
- Filtro por tema (opcional)
- Usa ExamCard para cada examen

**Paso 7.2:** Página de Examen (app/exam/[id]/page.tsx)
- Carga examen desde API
- Genera userId si no existe (localStorage)
- Renderiza ExamPlayer
- Al finalizar, redirect a resultados

**Paso 7.3:** Página de Resultados (app/exam/results/[examId]/page.tsx)
- Carga attempt desde API
- Renderiza ResultsDisplay
- Botón para volver a intentar
- Botón para ver historial

**Paso 7.4:** Dashboard (app/dashboard/page.tsx)
- Lista intentos del usuario (por userId)
- Muestra: fecha, examen, score
- Click para ver detalle

---

### Fase 8: Admin Panel

**Paso 8.1:** Admin Home (app/admin/page.tsx)
- Lista de todos los exámenes
- Botón "Subir nuevo examen"
- Opciones: Editar, Eliminar

**Paso 8.2:** Upload JSON (app/admin/upload/page.tsx)
- Form con file input
- Preview del JSON antes de subir
- Validación en frontend
- Submit a API /upload

**Paso 8.3:** Editar Examen (app/admin/exams/[id]/page.tsx)
- Editar título, duración, descripción
- Lista de preguntas
- Editar pregunta individual inline o en modal
- Agregar nueva pregunta
- Eliminar pregunta

**Paso 8.4:** Componentes Admin
- AdminExamList.tsx
- AdminQuestionForm.tsx
- JsonUploadForm.tsx

---

### Fase 9: Lógica de Examen General

**Paso 9.1:** Crear lógica para examen general
- Al crear un examen con subject="general"
- Combinar preguntas de todos los temas
- Distribución: 40 matemática, 40 lengua, 40 lectura, etc.
- Total: ~160-200 preguntas (como el oficial)
- Duración: 270 minutos (4.5 horas)

**Paso 9.2:** API para generar examen general dinámicamente
- Endpoint opcional: `/api/exams/generate-general`
- Selecciona preguntas random de cada tema

---

### Fase 10: Mejoras UX

**Paso 10.1:** LocalStorage para userId persistente
- Generar UUID en primer uso
- Usar para tracking de intentos

**Paso 10.2:** Guardar progreso (opcional)
- Guardar respuestas en localStorage mientras hace examen
- Recuperar si recarga la página

**Paso 10.3:** Notificaciones toast
- Usar react-hot-toast
- Confirmaciones al guardar, errores, etc.

**Paso 10.4:** Loading states
- Spinners mientras carga
- Skeleton loaders

---

### Fase 11: Deployment a Vercel

**Paso 11.1:** Configurar base de datos en producción
- Crear DB en Supabase (gratis) o Railway
- Obtener DATABASE_URL de producción

**Paso 11.2:** Configurar variables de entorno en Vercel
- DATABASE_URL
- NEXT_PUBLIC_APP_URL

**Paso 11.3:** Deploy
```bash
vercel --prod
```

**Paso 11.4:** Ejecutar migraciones en producción
```bash
npx prisma migrate deploy
```

---

## Archivos Críticos a Crear

### Configuración
1. `prisma/schema.prisma` - Esquema de BD
2. `lib/db.ts` - Cliente Prisma
3. `.env.local` - Variables de entorno
4. `tailwind.config.ts` - Config de Tailwind

### Backend (API Routes)
5. `app/api/exams/route.ts`
6. `app/api/exams/[id]/route.ts`
7. `app/api/upload/route.ts`
8. `app/api/questions/[id]/route.ts`
9. `app/api/attempts/route.ts`
10. `app/api/submit/route.ts`

### Frontend (Páginas)
11. `app/page.tsx` - Home
12. `app/exam/[id]/page.tsx` - Simulacro
13. `app/exam/results/[examId]/page.tsx` - Resultados
14. `app/dashboard/page.tsx` - Historial
15. `app/admin/page.tsx` - Admin home
16. `app/admin/upload/page.tsx` - Upload JSON
17. `app/admin/exams/[id]/page.tsx` - Editar examen

### Componentes
18. `components/ExamPlayer.tsx` - Motor del examen
19. `components/Timer.tsx` - Temporizador
20. `components/QuestionDisplay.tsx` - Display de pregunta
21. `components/Navigation.tsx` - Navegación
22. `components/ResultsDisplay.tsx` - Resultados
23. `components/JsonUploadForm.tsx` - Form upload
24. `components/ui/Button.tsx`, `Card.tsx`, `Input.tsx`

### Utils
25. `lib/types.ts` - Interfaces TypeScript
26. `lib/json-validator.ts` - Validación JSON
27. `lib/exam-utils.ts` - Lógica de calificación

---

## Verificación End-to-End

### Testing Manual
1. **Subir examen:**
   - Ir a `/admin/upload`
   - Subir JSON de ejemplo
   - Verificar que se crea en DB

2. **Realizar simulacro:**
   - Ir a `/`
   - Seleccionar examen
   - Responder preguntas
   - Ver timer funcionando
   - Finalizar examen

3. **Ver resultados:**
   - Revisar score
   - Ver preguntas correctas/incorrectas
   - Ver explicaciones

4. **Historial:**
   - Ir a `/dashboard`
   - Ver lista de intentos
   - Click para ver detalle

5. **Editar desde admin:**
   - Ir a `/admin/exams/[id]`
   - Editar una pregunta
   - Verificar cambio

### Testing de BD
```bash
npx prisma studio
```
- Verificar que Exams, Questions, Attempts se guardan correctamente

### Testing de Deploy
1. Hacer commit del código
2. Push a GitHub
3. Conectar repo en Vercel
4. Verificar que build pasa
5. Probar en producción

---

## Consideraciones Adicionales

### Seguridad
- Validar todos los JSONs antes de insertar en BD
- Sanitizar inputs del usuario
- Rate limiting en APIs (opcional con middleware)
- Admin protegido con password (fase futura)

### Performance
- Usar Server Components donde sea posible
- Lazy loading de imágenes
- Paginación en historial (si hay muchos intentos)
- Index en BD para queries frecuentes

### SEO
- Metadata en cada página
- Open Graph tags
- Sitemap (generado automáticamente con Next.js)

### Escalabilidad Futura
- Sistema de usuarios con autenticación (NextAuth.js)
- Roles: estudiante, profesor, admin
- Estadísticas avanzadas
- Comparación con otros usuarios
- Modo práctica (solo preguntas de un tema)
- Exámenes con límite de intentos

---

## Resumen de Dependencias

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@prisma/client": "^5.0.0",
    "zod": "^3.22.0",
    "date-fns": "^3.0.0",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.0.0",
    "prisma": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.0.0",
    "autoprefixer": "^10.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^15.0.0"
  }
}
```

---

## Orden de Ejecución Recomendado

1. **Setup (Fase 1-2):** Inicializar proyecto + DB
2. **Backend (Fase 3-4):** Types, utils, API routes
3. **UI Base (Fase 5):** Componentes base
4. **Funcionalidad Core (Fase 6-7):** Examen + Resultados
5. **Admin (Fase 8):** Panel de administración
6. **Polish (Fase 10):** UX improvements
7. **Deploy (Fase 11):** Producción en Vercel

---

## Notas Finales

Este plan está diseñado para ser ejecutado de forma incremental. Cada fase puede ser completada y testeada antes de pasar a la siguiente. El proyecto resultante será una plataforma funcional, escalable y fácil de mantener para simulacros del EXANI-II.

El plan prioriza funcionalidad sobre complejidad innecesaria, siguiendo las mejores prácticas de Next.js 15 y aprovechando al máximo las capacidades de Vercel para deployment automático.
