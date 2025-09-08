# Database Schema and API Specifications

## Database Schema (Prisma + MongoDB)

### User Model
```prisma
model User {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  email     String   @unique
  name      String
  avatar    String?
  role      UserRole @default(USER)
  settings  Json     @default("{}")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  projects      Project[]
  collaborations Collaboration[]
  comments      Comment[]
  sessions      Session[]
  activities    Activity[]

  @@map("users")
}

enum UserRole {
  USER
  ADMIN
  MODERATOR
}
```

### Project & Artboard Models
```prisma
model Project {
  id          String        @id @default(auto()) @map("_id") @db.ObjectId
  name        String
  description String?
  thumbnail   String?
  settings    Json          @default("{}")
  visibility  Visibility    @default(PRIVATE)
  status      ProjectStatus @default(ACTIVE)
  createdAt   DateTime      @default(now())
  updatedAt   DateTime      @updatedAt
  ownerId     String        @db.ObjectId

  // Relations
  owner          User            @relation(fields: [ownerId], references: [id])
  artboards      Artboard[]
  collaborations Collaboration[]
  comments       Comment[]
  versions       Version[]
  activities     Activity[]

  @@map("projects")
}

model Artboard {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  name      String
  width     Int
  height    Int
  x         Float    @default(0)
  y         Float    @default(0)
  objects   Json     @default("[]") // Vector objects data
  styles    Json     @default("{}") // Shared styles
  assets    Json     @default("[]") // Image assets
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  projectId String   @db.ObjectId

  // Relations
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@map("artboards")
}

enum Visibility {
  PRIVATE
  PUBLIC
  TEAM
}

enum ProjectStatus {
  ACTIVE
  ARCHIVED
  DELETED
}
```

### Collaboration Models
```prisma
model Collaboration {
  id          String           @id @default(auto()) @map("_id") @db.ObjectId
  role        CollaborationRole
  permissions Json             @default("{}")
  inviteStatus InviteStatus    @default(PENDING)
  invitedAt   DateTime         @default(now())
  joinedAt    DateTime?
  lastActive  DateTime?
  userId      String           @db.ObjectId
  projectId   String           @db.ObjectId

  // Relations
  user    User    @relation(fields: [userId], references: [id])
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@unique([userId, projectId])
  @@map("collaborations")
}

enum CollaborationRole {
  OWNER
  EDITOR
  VIEWER
  COMMENTER
}

enum InviteStatus {
  PENDING
  ACCEPTED
  DECLINED
}
```

### Real-time Session Management
```prisma
model Session {
  id          String    @id @default(auto()) @map("_id") @db.ObjectId
  cursor      Json?     // Cursor position {x, y}
  selection   Json?     // Selected objects
  viewport    Json?     // Current viewport bounds
  tool        String?   // Current tool
  isActive    Boolean   @default(true)
  lastPing    DateTime  @default(now())
  joinedAt    DateTime  @default(now())
  leftAt      DateTime?
  userId      String    @db.ObjectId
  projectId   String    @db.ObjectId
  artboardId  String?   @db.ObjectId

  // Relations
  user User @relation(fields: [userId], references: [id])

  @@map("sessions")
}
```

### Version Control System
```prisma
model Version {
  id          String      @id @default(auto()) @map("_id") @db.ObjectId
  name        String
  description String?
  snapshot    Json        // Complete project state
  changes     Json        @default("[]") // Change log
  type        VersionType @default(AUTO)
  createdBy   String      @db.ObjectId
  createdAt   DateTime    @default(now())
  projectId   String      @db.ObjectId

  // Relations
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@map("versions")
}

enum VersionType {
  AUTO
  MANUAL
  MILESTONE
  BRANCH
}
```

### Comments & Feedback
```prisma
model Comment {
  id        String        @id @default(auto()) @map("_id") @db.ObjectId
  content   String
  x         Float
  y         Float
  resolved  Boolean       @default(false)
  type      CommentType   @default(GENERAL)
  status    CommentStatus @default(OPEN)
  createdAt DateTime      @default(now())
  updatedAt DateTime      @updatedAt
  authorId  String        @db.ObjectId
  projectId String        @db.ObjectId
  objectId  String?       // Related canvas object

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

enum CommentType {
  GENERAL
  SUGGESTION
  ISSUE
  APPROVAL
}

enum CommentStatus {
  OPEN
  RESOLVED
  ARCHIVED
}
```

### Activity Tracking
```prisma
model Activity {
  id          String       @id @default(auto()) @map("_id") @db.ObjectId
  type        ActivityType
  description String
  metadata    Json         @default("{}")
  createdAt   DateTime     @default(now())
  userId      String       @db.ObjectId
  projectId   String       @db.ObjectId

  // Relations
  user    User    @relation(fields: [userId], references: [id])
  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)

  @@map("activities")
}

enum ActivityType {
  PROJECT_CREATED
  PROJECT_UPDATED
  ARTBOARD_CREATED
  ARTBOARD_UPDATED
  OBJECT_CREATED
  OBJECT_UPDATED
  OBJECT_DELETED
  COMMENT_ADDED
  USER_JOINED
  USER_LEFT
  VERSION_CREATED
  EXPORT_GENERATED
}
```

## REST API Specification

### Authentication Endpoints
```typescript
// POST /api/auth/login
interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

// POST /api/auth/register
interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

// POST /api/auth/refresh
interface RefreshRequest {
  refreshToken: string;
}

// POST /api/auth/logout
interface LogoutRequest {
  refreshToken: string;
}

// POST /api/auth/forgot-password
interface ForgotPasswordRequest {
  email: string;
}

// POST /api/auth/reset-password
interface ResetPasswordRequest {
  token: string;
  password: string;
  confirmPassword: string;
}
```

### Project Management API
```typescript
// GET /api/projects
interface ListProjectsQuery {
  page?: number;
  limit?: number;
  search?: string;
  status?: ProjectStatus;
  sortBy?: 'name' | 'updatedAt' | 'createdAt';
  sortOrder?: 'asc' | 'desc';
  includeArchived?: boolean;
}

interface ListProjectsResponse {
  projects: Project[];
  totalCount: number;
  page: number;
  limit: number;
  hasNextPage: boolean;
}

// POST /api/projects
interface CreateProjectRequest {
  name: string;
  description?: string;
  visibility?: Visibility;
  template?: string; // Template ID for project creation
}

// GET /api/projects/:id
interface GetProjectResponse {
  project: Project & {
    artboards: Artboard[];
    collaborations: (Collaboration & { user: User })[];
    activities: Activity[];
  };
}

// PATCH /api/projects/:id
interface UpdateProjectRequest {
  name?: string;
  description?: string;
  visibility?: Visibility;
  settings?: Record<string, any>;
}

// DELETE /api/projects/:id
// Returns 204 No Content

// POST /api/projects/:id/duplicate
interface DuplicateProjectRequest {
  name?: string;
  includeComments?: boolean;
  includeVersions?: boolean;
}
```

### Artboard Management API
```typescript
// GET /api/projects/:projectId/artboards
interface ListArtboardsResponse {
  artboards: Artboard[];
}

// POST /api/projects/:projectId/artboards
interface CreateArtboardRequest {
  name: string;
  width: number;
  height: number;
  x?: number;
  y?: number;
  template?: 'phone' | 'tablet' | 'desktop' | 'custom';
}

// PATCH /api/artboards/:id
interface UpdateArtboardRequest {
  name?: string;
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  objects?: any[]; // Vector objects
  styles?: Record<string, any>;
}

// DELETE /api/artboards/:id
// Returns 204 No Content

// POST /api/artboards/:id/duplicate
interface DuplicateArtboardRequest {
  name?: string;
  x?: number;
  y?: number;
}
```

### Collaboration API
```typescript
// GET /api/projects/:projectId/collaborators
interface ListCollaboratorsResponse {
  collaborations: (Collaboration & { user: User })[];
}

// POST /api/projects/:projectId/collaborators
interface InviteCollaboratorRequest {
  email: string;
  role: CollaborationRole;
  message?: string;
}

// PATCH /api/collaborations/:id
interface UpdateCollaborationRequest {
  role?: CollaborationRole;
  permissions?: Record<string, boolean>;
}

// DELETE /api/collaborations/:id
// Returns 204 No Content

// POST /api/collaborations/:id/accept
// Accept collaboration invitation

// POST /api/collaborations/:id/decline
// Decline collaboration invitation
```

### Comments API
```typescript
// GET /api/projects/:projectId/comments
interface ListCommentsQuery {
  resolved?: boolean;
  type?: CommentType;
  objectId?: string;
}

interface ListCommentsResponse {
  comments: (Comment & { author: User; replies: Reply[] })[];
}

// POST /api/projects/:projectId/comments
interface CreateCommentRequest {
  content: string;
  x: number;
  y: number;
  type?: CommentType;
  objectId?: string;
}

// PATCH /api/comments/:id
interface UpdateCommentRequest {
  content?: string;
  resolved?: boolean;
  status?: CommentStatus;
}

// DELETE /api/comments/:id
// Returns 204 No Content

// POST /api/comments/:id/replies
interface CreateReplyRequest {
  content: string;
}
```

### Export API
```typescript
// POST /api/artboards/:id/export
interface ExportRequest {
  format: 'png' | 'jpg' | 'svg' | 'pdf';
  scale?: number; // 1x, 2x, 3x
  quality?: number; // For JPG (1-100)
  background?: string; // Hex color or 'transparent'
  bounds?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface ExportResponse {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  downloadUrl?: string;
  estimatedTime?: number; // Seconds
}

// GET /api/export/:jobId
interface ExportStatusResponse {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress?: number; // 0-100
  downloadUrl?: string;
  expiresAt?: string; // ISO date
  error?: string;
}

// POST /api/projects/:id/export-all
interface ExportAllRequest {
  format: 'png' | 'jpg' | 'svg' | 'pdf';
  scale?: number;
  includeComments?: boolean;
  archive?: boolean; // Create ZIP file
}
```

### Version Control API
```typescript
// GET /api/projects/:projectId/versions
interface ListVersionsQuery {
  page?: number;
  limit?: number;
  type?: VersionType;
}

interface ListVersionsResponse {
  versions: Version[];
  totalCount: number;
  page: number;
  limit: number;
}

// POST /api/projects/:projectId/versions
interface CreateVersionRequest {
  name: string;
  description?: string;
  type?: VersionType;
}

// GET /api/versions/:id
interface GetVersionResponse {
  version: Version;
  diff?: {
    added: any[];
    modified: any[];
    removed: any[];
  };
}

// POST /api/versions/:id/restore
interface RestoreVersionRequest {
  createBackup?: boolean;
}

// DELETE /api/versions/:id
// Returns 204 No Content
```

### Search API
```typescript
// GET /api/search
interface SearchQuery {
  q: string; // Search query
  type?: 'projects' | 'objects' | 'comments' | 'all';
  projectId?: string; // Limit to specific project
  limit?: number;
  page?: number;
}

interface SearchResponse {
  results: SearchResult[];
  totalCount: number;
  suggestions?: string[];
}

interface SearchResult {
  type: 'project' | 'artboard' | 'object' | 'comment';
  id: string;
  title: string;
  description?: string;
  thumbnail?: string;
  relevance: number; // 0-1
  project?: {
    id: string;
    name: string;
  };
}
```

## WebSocket Event Specifications

### Connection Events
```typescript
// Client -> Server
interface JoinProjectEvent {
  projectId: string;
  artboardId?: string;
  cursor?: { x: number; y: number };
}

interface LeaveProjectEvent {
  projectId: string;
}

// Server -> Client
interface UserJoinedEvent {
  user: {
    id: string;
    name: string;
    avatar: string;
  };
  cursor?: { x: number; y: number };
  timestamp: number;
}

interface UserLeftEvent {
  userId: string;
  timestamp: number;
}
```

### Canvas Operations
```typescript
// Client -> Server
interface CanvasOperationEvent {
  type: 'create' | 'update' | 'delete' | 'move' | 'transform';
  objectId: string;
  artboardId: string;
  data: any;
  timestamp: number;
  clientId: string; // For deduplication
}

// Server -> Client (broadcast)
interface CanvasOperationBroadcast {
  operation: CanvasOperationEvent;
  userId: string;
  userName: string;
  transformedData?: any; // OT transformed data
}
```

### Real-time Cursors
```typescript
// Client -> Server
interface CursorMoveEvent {
  x: number;
  y: number;
  artboardId?: string;
  tool?: string;
  selection?: string[]; // Selected object IDs
}

// Server -> Client (broadcast)
interface CursorUpdateEvent {
  userId: string;
  userName: string;
  avatar: string;
  x: number;
  y: number;
  artboardId?: string;
  tool?: string;
  selection?: string[];
  timestamp: number;
}
```

### Comments Events
```typescript
// Client -> Server
interface AddCommentEvent {
  content: string;
  x: number;
  y: number;
  artboardId: string;
  objectId?: string;
  type?: CommentType;
}

// Server -> Client (broadcast)
interface CommentAddedEvent {
  comment: Comment & { author: User };
  timestamp: number;
}

interface CommentUpdatedEvent {
  commentId: string;
  updates: Partial<Comment>;
  timestamp: number;
}
```

### Voice/Video Chat Events
```typescript
// Client -> Server
interface JoinVoiceChatEvent {
  projectId: string;
  mediaConstraints: {
    audio: boolean;
    video: boolean;
  };
}

interface LeaveVoiceChatEvent {
  projectId: string;
}

// WebRTC Signaling
interface RTCOfferEvent {
  targetUserId: string;
  offer: RTCSessionDescriptionInit;
}

interface RTCAnswerEvent {
  targetUserId: string;
  answer: RTCSessionDescriptionInit;
}

interface RTCIceCandidateEvent {
  targetUserId: string;
  candidate: RTCIceCandidateInit;
}
```

### Error Handling
```typescript
interface ErrorEvent {
  code: string;
  message: string;
  details?: any;
  timestamp: number;
}

// Common error codes
const ERROR_CODES = {
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  PROJECT_NOT_FOUND: 'PROJECT_NOT_FOUND',
  ARTBOARD_NOT_FOUND: 'ARTBOARD_NOT_FOUND',
  INVALID_OPERATION: 'INVALID_OPERATION',
  RATE_LIMITED: 'RATE_LIMITED',
  INTERNAL_ERROR: 'INTERNAL_ERROR'
} as const;
```

## TypeScript Definitions

### Canvas Object Types
```typescript
interface VectorObject {
  id: string;
  type: ObjectType;
  name?: string;
  visible: boolean;
  locked: boolean;
  opacity: number;
  transform: Transform;
  style: ObjectStyle;
  properties: Record<string, any>;
  metadata?: Record<string, any>;
  createdAt: number;
  updatedAt: number;
}

type ObjectType = 
  | 'rectangle'
  | 'circle'
  | 'ellipse'
  | 'polygon'
  | 'path'
  | 'text'
  | 'image'
  | 'group'
  | 'frame'
  | 'component'
  | 'instance';

interface Transform {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  scaleX: number;
  scaleY: number;
  skewX: number;
  skewY: number;
}

interface ObjectStyle {
  fill?: Fill;
  stroke?: Stroke;
  shadow?: Shadow[];
  blur?: Blur;
  blendMode?: BlendMode;
}

interface Fill {
  type: 'solid' | 'gradient' | 'image' | 'pattern';
  color?: string;
  gradient?: Gradient;
  image?: ImageFill;
  opacity: number;
}

interface Stroke {
  color: string;
  width: number;
  position: 'inside' | 'outside' | 'center';
  dashPattern?: number[];
  lineCap: 'butt' | 'round' | 'square';
  lineJoin: 'miter' | 'round' | 'bevel';
  opacity: number;
}
```

### Animation Types
```typescript
interface Animation {
  id: string;
  name: string;
  duration: number; // milliseconds
  easing: EasingFunction;
  keyframes: Keyframe[];
  loop: boolean;
  autoplay: boolean;
  delay: number;
}

interface Keyframe {
  time: number; // 0-1 (percentage of duration)
  properties: Record<string, any>;
  easing?: EasingFunction;
}

type EasingFunction = 
  | 'linear'
  | 'ease'
  | 'ease-in'
  | 'ease-out'
  | 'ease-in-out'
  | 'cubic-bezier'
  | { type: 'cubic-bezier'; values: [number, number, number, number] }
  | { type: 'spring'; tension: number; friction: number };

interface Transition {
  property: string;
  duration: number;
  easing: EasingFunction;
  delay: number;
}
```

### Collaboration Types
```typescript
interface CollaborationState {
  users: CollaboratingUser[];
  cursors: Map<string, CursorState>;
  selections: Map<string, SelectionState>;
  activeOperations: Map<string, CanvasOperation>;
}

interface CollaboratingUser {
  id: string;
  name: string;
  avatar: string;
  color: string; // Unique color for this user
  isOnline: boolean;
  lastSeen: number;
  permissions: UserPermissions;
}

interface CursorState {
  userId: string;
  x: number;
  y: number;
  artboardId?: string;
  tool?: string;
  timestamp: number;
}

interface SelectionState {
  userId: string;
  objectIds: string[];
  artboardId: string;
  timestamp: number;
}

interface UserPermissions {
  canEdit: boolean;
  canComment: boolean;
  canExport: boolean;
  canInvite: boolean;
  canManageProject: boolean;
}
```

This comprehensive database schema and API specification provides the foundation for building a production-ready Figma-like application with all the advanced features mentioned in the requirements.