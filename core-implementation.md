# Core Component Implementation Examples

## React Native Mobile Components

### Canvas Component with SVG Integration
```typescript
// src/components/Canvas/CanvasView.tsx
import React, { useRef, useCallback, useEffect, useState } from 'react';
import { View, PanResponder, Dimensions, StyleSheet } from 'react-native';
import Svg, { G, Rect, Circle, Path, Text as SvgText } from 'react-native-svg';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  useAnimatedGestureHandler,
  runOnJS,
  withSpring,
} from 'react-native-reanimated';
import {
  PanGestureHandler,
  PinchGestureHandler,
  State,
  PanGestureHandlerGestureEvent,
  PinchGestureHandlerGestureEvent,
} from 'react-native-gesture-handler';

interface CanvasViewProps {
  objects: VectorObject[];
  selectedObjectIds: string[];
  currentTool: string;
  onObjectCreate: (object: VectorObject) => void;
  onObjectUpdate: (id: string, updates: Partial<VectorObject>) => void;
  onObjectSelect: (ids: string[]) => void;
  onCanvasChange: (operation: CanvasOperation) => void;
}

export const CanvasView: React.FC<CanvasViewProps> = ({
  objects,
  selectedObjectIds,
  currentTool,
  onObjectCreate,
  onObjectUpdate,
  onObjectSelect,
  onCanvasChange,
}) => {
  const { width, height } = Dimensions.get('window');
  
  // Canvas transform values
  const scale = useSharedValue(1);
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  
  // Drawing state
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentPath, setCurrentPath] = useState<string>('');
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);

  // Pan gesture handler for canvas panning
  const panGestureHandler = useAnimatedGestureHandler<PanGestureHandlerGestureEvent>({
    onStart: (event) => {
      if (currentTool === 'pan') {
        // Start panning
      }
    },
    onActive: (event) => {
      if (currentTool === 'pan') {
        translateX.value = event.translationX;
        translateY.value = event.translationY;
      }
    },
    onEnd: () => {
      if (currentTool === 'pan') {
        translateX.value = withSpring(translateX.value);
        translateY.value = withSpring(translateY.value);
      }
    },
  });

  // Pinch gesture handler for zooming
  const pinchGestureHandler = useAnimatedGestureHandler<PinchGestureHandlerGestureEvent>({
    onStart: () => {
      // Store initial scale
    },
    onActive: (event) => {
      scale.value = Math.max(0.1, Math.min(5, event.scale));
    },
    onEnd: () => {
      scale.value = withSpring(scale.value);
    },
  });

  // Animated style for canvas transformation
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  // Handle touch events for drawing
  const handleTouchStart = useCallback((event: any) => {
    const { locationX, locationY } = event.nativeEvent;
    
    switch (currentTool) {
      case 'rectangle':
      case 'circle':
        setStartPoint({ x: locationX, y: locationY });
        setIsDrawing(true);
        break;
      case 'pen':
        setCurrentPath(`M${locationX},${locationY}`);
        setIsDrawing(true);
        break;
      case 'select':
        handleObjectSelection(locationX, locationY);
        break;
    }
  }, [currentTool]);

  const handleTouchMove = useCallback((event: any) => {
    if (!isDrawing) return;
    
    const { locationX, locationY } = event.nativeEvent;
    
    switch (currentTool) {
      case 'pen':
        setCurrentPath(prev => `${prev} L${locationX},${locationY}`);
        break;
    }
  }, [isDrawing, currentTool]);

  const handleTouchEnd = useCallback((event: any) => {
    if (!isDrawing) return;
    
    const { locationX, locationY } = event.nativeEvent;
    
    switch (currentTool) {
      case 'rectangle':
        if (startPoint) {
          const newRect: VectorObject = {
            id: generateId(),
            type: 'rectangle',
            x: Math.min(startPoint.x, locationX),
            y: Math.min(startPoint.y, locationY),
            width: Math.abs(locationX - startPoint.x),
            height: Math.abs(locationY - startPoint.y),
            fill: '#3B82F6',
            stroke: '#1E40AF',
            strokeWidth: 2,
            opacity: 1,
            rotation: 0,
            visible: true,
            locked: false,
          };
          onObjectCreate(newRect);
        }
        break;
      
      case 'circle':
        if (startPoint) {
          const radius = Math.sqrt(
            Math.pow(locationX - startPoint.x, 2) + Math.pow(locationY - startPoint.y, 2)
          );
          const newCircle: VectorObject = {
            id: generateId(),
            type: 'circle',
            x: startPoint.x,
            y: startPoint.y,
            radius,
            fill: '#10B981',
            stroke: '#047857',
            strokeWidth: 2,
            opacity: 1,
            rotation: 0,
            visible: true,
            locked: false,
          };
          onObjectCreate(newCircle);
        }
        break;
      
      case 'pen':
        const newPath: VectorObject = {
          id: generateId(),
          type: 'path',
          path: currentPath,
          fill: 'none',
          stroke: '#EF4444',
          strokeWidth: 3,
          opacity: 1,
          rotation: 0,
          visible: true,
          locked: false,
        };
        onObjectCreate(newPath);
        setCurrentPath('');
        break;
    }
    
    setIsDrawing(false);
    setStartPoint(null);
  }, [isDrawing, currentTool, startPoint, currentPath]);

  // Handle object selection
  const handleObjectSelection = useCallback((x: number, y: number) => {
    const selectedObject = objects.find(obj => isPointInObject(x, y, obj));
    if (selectedObject) {
      onObjectSelect([selectedObject.id]);
    } else {
      onObjectSelect([]);
    }
  }, [objects, onObjectSelect]);

  // Render vector objects
  const renderObjects = () => {
    return objects.map(obj => {
      const isSelected = selectedObjectIds.includes(obj.id);
      
      switch (obj.type) {
        case 'rectangle':
          return (
            <Rect
              key={obj.id}
              x={obj.x}
              y={obj.y}
              width={obj.width}
              height={obj.height}
              fill={obj.fill}
              stroke={isSelected ? '#FF6B35' : obj.stroke}
              strokeWidth={isSelected ? obj.strokeWidth + 1 : obj.strokeWidth}
              opacity={obj.opacity}
              transform={`rotate(${obj.rotation} ${obj.x + obj.width/2} ${obj.y + obj.height/2})`}
            />
          );
        
        case 'circle':
          return (
            <Circle
              key={obj.id}
              cx={obj.x}
              cy={obj.y}
              r={obj.radius}
              fill={obj.fill}
              stroke={isSelected ? '#FF6B35' : obj.stroke}
              strokeWidth={isSelected ? obj.strokeWidth + 1 : obj.strokeWidth}
              opacity={obj.opacity}
              transform={`rotate(${obj.rotation} ${obj.x} ${obj.y})`}
            />
          );
        
        case 'path':
          return (
            <Path
              key={obj.id}
              d={obj.path}
              fill={obj.fill}
              stroke={isSelected ? '#FF6B35' : obj.stroke}
              strokeWidth={isSelected ? obj.strokeWidth + 1 : obj.strokeWidth}
              opacity={obj.opacity}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          );
        
        case 'text':
          return (
            <SvgText
              key={obj.id}
              x={obj.x}
              y={obj.y}
              fontSize={obj.fontSize || 16}
              fontFamily={obj.fontFamily || 'Arial'}
              fill={obj.fill}
              opacity={obj.opacity}
              transform={`rotate(${obj.rotation} ${obj.x} ${obj.y})`}
            >
              {obj.text}
            </SvgText>
          );
        
        default:
          return null;
      }
    });
  };

  return (
    <View style={styles.container}>
      <PinchGestureHandler onGestureEvent={pinchGestureHandler}>
        <Animated.View style={[styles.canvasContainer, animatedStyle]}>
          <PanGestureHandler 
            onGestureEvent={panGestureHandler}
            minPointers={currentTool === 'pan' ? 1 : 2}
          >
            <Animated.View
              style={styles.canvas}
              onTouchStart={handleTouchStart}
              onTouchMove={handleTouchMove}
              onTouchEnd={handleTouchEnd}
            >
              <Svg width={width} height={height}>
                <G>
                  {/* Grid background */}
                  <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#E5E7EB" strokeWidth="0.5"/>
                    </pattern>
                  </defs>
                  <Rect width="100%" height="100%" fill="url(#grid)" />
                  
                  {/* Render all objects */}
                  {renderObjects()}
                  
                  {/* Current drawing preview */}
                  {isDrawing && currentTool === 'pen' && (
                    <Path
                      d={currentPath}
                      fill="none"
                      stroke="#EF4444"
                      strokeWidth={3}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      opacity={0.7}
                    />
                  )}
                </G>
              </Svg>
            </Animated.View>
          </PanGestureHandler>
        </Animated.View>
      </PinchGestureHandler>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  canvasContainer: {
    flex: 1,
  },
  canvas: {
    flex: 1,
  },
});

// Helper functions
const generateId = (): string => {
  return `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

const isPointInObject = (x: number, y: number, obj: VectorObject): boolean => {
  switch (obj.type) {
    case 'rectangle':
      return x >= obj.x && x <= obj.x + obj.width && y >= obj.y && y <= obj.y + obj.height;
    case 'circle':
      const distance = Math.sqrt(Math.pow(x - obj.x, 2) + Math.pow(y - obj.y, 2));
      return distance <= obj.radius;
    default:
      return false;
  }
};
```

### Real-Time Collaboration Service
```typescript
// src/services/CollaborationService.ts
import io, { Socket } from 'socket.io-client';
import { OperationalTransform } from './OperationalTransform';

export interface CollaborationUser {
  id: string;
  name: string;
  avatar: string;
  color: string;
  cursor?: { x: number; y: number };
  selection?: string[];
}

export interface CanvasOperation {
  id: string;
  type: 'create' | 'update' | 'delete' | 'transform';
  objectId: string;
  data: any;
  userId: string;
  timestamp: number;
  clientId: string;
}

export class CollaborationService {
  private socket: Socket | null = null;
  private projectId: string | null = null;
  private userId: string | null = null;
  private clientId: string;
  private otEngine: OperationalTransform;
  
  private onUsersUpdate: ((users: CollaborationUser[]) => void) | null = null;
  private onCursorUpdate: ((userId: string, cursor: { x: number; y: number }) => void) | null = null;
  private onOperationReceived: ((operation: CanvasOperation) => void) | null = null;
  private onCommentReceived: ((comment: any) => void) | null = null;

  constructor() {
    this.clientId = this.generateClientId();
    this.otEngine = new OperationalTransform();
  }

  // Connect to collaboration server
  async connect(apiUrl: string, token: string): Promise<void> {
    try {
      this.socket = io(apiUrl, {
        auth: { token },
        transports: ['websocket', 'polling'],
      });

      this.setupEventHandlers();
      
      return new Promise((resolve, reject) => {
        this.socket!.on('connect', () => {
          console.log('Connected to collaboration server');
          resolve();
        });

        this.socket!.on('connect_error', (error) => {
          console.error('Connection failed:', error);
          reject(error);
        });
      });
    } catch (error) {
      console.error('Failed to connect to collaboration server:', error);
      throw error;
    }
  }

  // Join a project room
  async joinProject(projectId: string, userId: string): Promise<void> {
    if (!this.socket) throw new Error('Not connected to server');

    this.projectId = projectId;
    this.userId = userId;

    this.socket.emit('project:join', {
      projectId,
      userId,
      clientId: this.clientId,
    });
  }

  // Leave current project
  leaveProject(): void {
    if (!this.socket || !this.projectId) return;

    this.socket.emit('project:leave', {
      projectId: this.projectId,
      userId: this.userId,
    });

    this.projectId = null;
    this.userId = null;
  }

  // Send canvas operation to other collaborators
  broadcastOperation(operation: Omit<CanvasOperation, 'id' | 'clientId' | 'timestamp'>): void {
    if (!this.socket || !this.projectId) return;

    const fullOperation: CanvasOperation = {
      ...operation,
      id: this.generateOperationId(),
      clientId: this.clientId,
      timestamp: Date.now(),
    };

    this.socket.emit('canvas:operation', {
      projectId: this.projectId,
      operation: fullOperation,
    });
  }

  // Send cursor position
  updateCursor(x: number, y: number, tool?: string, selection?: string[]): void {
    if (!this.socket || !this.projectId) return;

    this.socket.emit('cursor:move', {
      projectId: this.projectId,
      userId: this.userId,
      x,
      y,
      tool,
      selection,
      timestamp: Date.now(),
    });
  }

  // Send comment
  addComment(x: number, y: number, content: string, objectId?: string): void {
    if (!this.socket || !this.projectId) return;

    this.socket.emit('comment:add', {
      projectId: this.projectId,
      userId: this.userId,
      x,
      y,
      content,
      objectId,
      timestamp: Date.now(),
    });
  }

  // Setup event handlers
  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Project state updates
    this.socket.on('project:state', (data) => {
      console.log('Received project state:', data);
      // Handle initial project state
    });

    // User joined/left events
    this.socket.on('users:update', (users: CollaborationUser[]) => {
      this.onUsersUpdate?.(users);
    });

    // Cursor updates
    this.socket.on('cursor:update', (data) => {
      if (data.userId !== this.userId) {
        this.onCursorUpdate?.(data.userId, { x: data.x, y: data.y });
      }
    });

    // Canvas operations
    this.socket.on('canvas:operation', (data) => {
      if (data.operation.clientId !== this.clientId) {
        // Apply operational transform
        const transformedOperation = this.otEngine.transform(data.operation);
        this.onOperationReceived?.(transformedOperation);
      }
    });

    // Comments
    this.socket.on('comment:added', (comment) => {
      this.onCommentReceived?.(comment);
    });

    // Error handling
    this.socket.on('error', (error) => {
      console.error('Collaboration error:', error);
    });

    // Connection events
    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from collaboration server:', reason);
    });

    this.socket.on('reconnect', () => {
      console.log('Reconnected to collaboration server');
      // Rejoin project if we were in one
      if (this.projectId && this.userId) {
        this.joinProject(this.projectId, this.userId);
      }
    });
  }

  // Event listeners
  onUsersChanged(callback: (users: CollaborationUser[]) => void): void {
    this.onUsersUpdate = callback;
  }

  onCursorChanged(callback: (userId: string, cursor: { x: number; y: number }) => void): void {
    this.onCursorUpdate = callback;
  }

  onOperationReceived(callback: (operation: CanvasOperation) => void): void {
    this.onOperationReceived = callback;
  }

  onCommentReceived(callback: (comment: any) => void): void {
    this.onCommentReceived = callback;
  }

  // Cleanup
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateOperationId(): string {
    return `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

## Node.js Backend Implementation

### WebSocket Server with Socket.IO
```typescript
// src/services/SocketService.ts
import { Server as SocketIOServer } from 'socket.io';
import { Server as HTTPServer } from 'http';
import { Redis } from 'ioredis';
import { PrismaClient } from '@prisma/client';
import { OperationalTransformEngine } from './OperationalTransformEngine';
import { AuthService } from './AuthService';

interface CollaborationRoom {
  projectId: string;
  users: Map<string, CollaborationUser>;
  operations: CanvasOperation[];
  lastActivity: number;
}

export class SocketService {
  private io: SocketIOServer;
  private redis: Redis;
  private prisma: PrismaClient;
  private otEngine: OperationalTransformEngine;
  private authService: AuthService;
  private rooms: Map<string, CollaborationRoom> = new Map();

  constructor(httpServer: HTTPServer) {
    this.io = new SocketIOServer(httpServer, {
      cors: {
        origin: process.env.CORS_ORIGIN?.split(',') || '*',
        methods: ['GET', 'POST'],
        credentials: true,
      },
      transports: ['websocket', 'polling'],
    });

    this.redis = new Redis(process.env.REDIS_URL!);
    this.prisma = new PrismaClient();
    this.otEngine = new OperationalTransformEngine();
    this.authService = new AuthService();

    this.setupEventHandlers();
    this.setupMiddleware();
  }

  private setupMiddleware(): void {
    // Authentication middleware
    this.io.use(async (socket, next) => {
      try {
        const token = socket.handshake.auth.token;
        if (!token) {
          throw new Error('No authentication token provided');
        }

        const user = await this.authService.verifyToken(token);
        socket.data.user = user;
        next();
      } catch (error) {
        next(new Error('Authentication failed'));
      }
    });

    // Rate limiting middleware
    this.io.use(async (socket, next) => {
      const userId = socket.data.user.id;
      const key = `rate_limit:${userId}`;
      
      const current = await this.redis.incr(key);
      if (current === 1) {
        await this.redis.expire(key, 60); // 1 minute window
      }
      
      if (current > 100) { // Max 100 requests per minute
        next(new Error('Rate limit exceeded'));
        return;
      }
      
      next();
    });
  }

  private setupEventHandlers(): void {
    this.io.on('connection', (socket) => {
      console.log(`User ${socket.data.user.id} connected`);

      // Join project room
      socket.on('project:join', async (data) => {
        try {
          await this.handleProjectJoin(socket, data);
        } catch (error) {
          socket.emit('error', { message: 'Failed to join project', error: error.message });
        }
      });

      // Leave project room
      socket.on('project:leave', async (data) => {
        try {
          await this.handleProjectLeave(socket, data);
        } catch (error) {
          socket.emit('error', { message: 'Failed to leave project', error: error.message });
        }
      });

      // Canvas operations
      socket.on('canvas:operation', async (data) => {
        try {
          await this.handleCanvasOperation(socket, data);
        } catch (error) {
          socket.emit('error', { message: 'Failed to process operation', error: error.message });
        }
      });

      // Cursor movement
      socket.on('cursor:move', async (data) => {
        try {
          await this.handleCursorMove(socket, data);
        } catch (error) {
          console.error('Cursor move error:', error);
        }
      });

      // Comments
      socket.on('comment:add', async (data) => {
        try {
          await this.handleCommentAdd(socket, data);
        } catch (error) {
          socket.emit('error', { message: 'Failed to add comment', error: error.message });
        }
      });

      // Voice/Video chat
      socket.on('voice:join', async (data) => {
        try {
          await this.handleVoiceJoin(socket, data);
        } catch (error) {
          socket.emit('error', { message: 'Failed to join voice chat', error: error.message });
        }
      });

      // WebRTC signaling
      socket.on('rtc:offer', (data) => {
        socket.to(data.targetUserId).emit('rtc:offer', {
          fromUserId: socket.data.user.id,
          offer: data.offer,
        });
      });

      socket.on('rtc:answer', (data) => {
        socket.to(data.targetUserId).emit('rtc:answer', {
          fromUserId: socket.data.user.id,
          answer: data.answer,
        });
      });

      socket.on('rtc:ice-candidate', (data) => {
        socket.to(data.targetUserId).emit('rtc:ice-candidate', {
          fromUserId: socket.data.user.id,
          candidate: data.candidate,
        });
      });

      // Disconnect handling
      socket.on('disconnect', (reason) => {
        console.log(`User ${socket.data.user.id} disconnected: ${reason}`);
        this.handleDisconnect(socket);
      });
    });
  }

  private async handleProjectJoin(socket: any, data: any): Promise<void> {
    const { projectId } = data;
    const userId = socket.data.user.id;

    // Verify user has access to project
    const collaboration = await this.prisma.collaboration.findUnique({
      where: {
        userId_projectId: { userId, projectId },
      },
      include: {
        project: true,
        user: true,
      },
    });

    if (!collaboration) {
      throw new Error('Access denied to project');
    }

    // Join socket room
    await socket.join(projectId);

    // Create or get collaboration room
    let room = this.rooms.get(projectId);
    if (!room) {
      room = {
        projectId,
        users: new Map(),
        operations: [],
        lastActivity: Date.now(),
      };
      this.rooms.set(projectId, room);
    }

    // Add user to room
    const collaborationUser: CollaborationUser = {
      id: userId,
      name: socket.data.user.name,
      avatar: socket.data.user.avatar,
      color: this.generateUserColor(userId),
      socketId: socket.id,
      role: collaboration.role,
      joinedAt: Date.now(),
    };

    room.users.set(userId, collaborationUser);
    room.lastActivity = Date.now();

    // Create session record
    await this.prisma.session.create({
      data: {
        userId,
        projectId,
        isActive: true,
      },
    });

    // Send current project state to joining user
    const projectState = await this.getProjectState(projectId);
    socket.emit('project:state', projectState);

    // Notify other users about new user
    socket.to(projectId).emit('user:joined', collaborationUser);

    // Send updated user list to all users in room
    const users = Array.from(room.users.values());
    this.io.to(projectId).emit('users:update', users);

    console.log(`User ${userId} joined project ${projectId}`);
  }

  private async handleProjectLeave(socket: any, data: any): Promise<void> {
    const { projectId } = data;
    const userId = socket.data.user.id;

    await socket.leave(projectId);

    // Remove user from room
    const room = this.rooms.get(projectId);
    if (room) {
      room.users.delete(userId);
      room.lastActivity = Date.now();

      // If room is empty, clean it up after a delay
      if (room.users.size === 0) {
        setTimeout(() => {
          if (room.users.size === 0) {
            this.rooms.delete(projectId);
          }
        }, 60000); // 1 minute delay
      }
    }

    // Update session record
    await this.prisma.session.updateMany({
      where: {
        userId,
        projectId,
        isActive: true,
      },
      data: {
        isActive: false,
        leftAt: new Date(),
      },
    });

    // Notify other users
    socket.to(projectId).emit('user:left', { userId });

    // Send updated user list
    if (room) {
      const users = Array.from(room.users.values());
      this.io.to(projectId).emit('users:update', users);
    }

    console.log(`User ${userId} left project ${projectId}`);
  }

  private async handleCanvasOperation(socket: any, data: any): Promise<void> {
    const { projectId, operation } = data;
    const userId = socket.data.user.id;

    // Verify user has edit permission
    const collaboration = await this.prisma.collaboration.findUnique({
      where: {
        userId_projectId: { userId, projectId },
      },
    });

    if (!collaboration || !['OWNER', 'EDITOR'].includes(collaboration.role)) {
      throw new Error('Insufficient permissions to edit project');
    }

    // Apply operational transform
    const room = this.rooms.get(projectId);
    if (room) {
      const transformedOperation = await this.otEngine.transformOperation(
        operation,
        room.operations
      );

      // Add to room operations history
      room.operations.push(transformedOperation);
      room.lastActivity = Date.now();

      // Keep only recent operations (last 1000)
      if (room.operations.length > 1000) {
        room.operations = room.operations.slice(-1000);
      }

      // Broadcast to other users in room
      socket.to(projectId).emit('canvas:operation', {
        operation: transformedOperation,
        userId,
      });

      // Persist operation to database (async)
      this.persistOperation(projectId, transformedOperation).catch(console.error);

      // Update project's updatedAt timestamp
      this.prisma.project.update({
        where: { id: projectId },
        data: { updatedAt: new Date() },
      }).catch(console.error);
    }
  }

  private async handleCursorMove(socket: any, data: any): Promise<void> {
    const { projectId, x, y, tool, selection } = data;
    const userId = socket.data.user.id;

    // Update user cursor in room
    const room = this.rooms.get(projectId);
    if (room) {
      const user = room.users.get(userId);
      if (user) {
        user.cursor = { x, y };
        user.tool = tool;
        user.selection = selection;
      }
    }

    // Broadcast cursor update to other users
    socket.to(projectId).emit('cursor:update', {
      userId,
      x,
      y,
      tool,
      selection,
      timestamp: Date.now(),
    });

    // Update session with cursor position
    await this.redis.setex(
      `cursor:${userId}:${projectId}`,
      30, // 30 second expiry
      JSON.stringify({ x, y, tool, selection, timestamp: Date.now() })
    );
  }

  private async handleCommentAdd(socket: any, data: any): Promise<void> {
    const { projectId, x, y, content, objectId } = data;
    const userId = socket.data.user.id;

    // Create comment in database
    const comment = await this.prisma.comment.create({
      data: {
        content,
        x,
        y,
        objectId,
        authorId: userId,
        projectId,
      },
      include: {
        author: true,
      },
    });

    // Broadcast comment to all users in project
    this.io.to(projectId).emit('comment:added', comment);

    // Log activity
    await this.prisma.activity.create({
      data: {
        type: 'COMMENT_ADDED',
        description: `${socket.data.user.name} added a comment`,
        metadata: { commentId: comment.id, x, y },
        userId,
        projectId,
      },
    });
  }

  private async handleVoiceJoin(socket: any, data: any): Promise<void> {
    const { projectId, mediaConstraints } = data;
    const userId = socket.data.user.id;

    // Join voice room
    await socket.join(`voice:${projectId}`);

    // Notify other users in voice chat
    socket.to(`voice:${projectId}`).emit('voice:user-joined', {
      userId,
      name: socket.data.user.name,
      mediaConstraints,
    });

    console.log(`User ${userId} joined voice chat for project ${projectId}`);
  }

  private handleDisconnect(socket: any): void {
    const userId = socket.data.user.id;

    // Clean up user from all rooms
    for (const [projectId, room] of this.rooms.entries()) {
      if (room.users.has(userId)) {
        room.users.delete(userId);
        room.lastActivity = Date.now();

        // Notify other users
        socket.to(projectId).emit('user:left', { userId });

        // Update user list
        const users = Array.from(room.users.values());
        this.io.to(projectId).emit('users:update', users);
      }
    }

    // Update all active sessions for this user
    this.prisma.session.updateMany({
      where: {
        userId,
        isActive: true,
      },
      data: {
        isActive: false,
        leftAt: new Date(),
      },
    }).catch(console.error);
  }

  private async getProjectState(projectId: string): Promise<any> {
    const project = await this.prisma.project.findUnique({
      where: { id: projectId },
      include: {
        artboards: true,
        collaborations: {
          include: { user: true },
        },
      },
    });

    return project;
  }

  private async persistOperation(projectId: string, operation: CanvasOperation): Promise<void> {
    // Update artboard with operation
    // This is a simplified version - in reality, you'd apply the operation to the artboard's objects
    await this.prisma.artboard.updateMany({
      where: { projectId },
      data: {
        updatedAt: new Date(),
        // objects: would need to apply operation to existing objects
      },
    });
  }

  private generateUserColor(userId: string): string {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
      '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    ];
    
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      hash = userId.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    return colors[Math.abs(hash) % colors.length];
  }
}
```

### Operational Transform Engine
```typescript
// src/services/OperationalTransformEngine.ts
export interface Operation {
  id: string;
  type: 'create' | 'update' | 'delete' | 'transform';
  objectId: string;
  data: any;
  userId: string;
  timestamp: number;
  clientId: string;
  dependencies?: string[]; // IDs of operations this depends on
}

export class OperationalTransformEngine {
  private operationHistory: Map<string, Operation> = new Map();

  async transformOperation(
    incomingOp: Operation,
    concurrentOps: Operation[]
  ): Promise<Operation> {
    // Find concurrent operations that need to be transformed against
    const conflictingOps = concurrentOps.filter(op => 
      op.objectId === incomingOp.objectId && 
      op.timestamp < incomingOp.timestamp &&
      op.clientId !== incomingOp.clientId
    );

    if (conflictingOps.length === 0) {
      return incomingOp; // No conflicts, return as-is
    }

    let transformedOp = { ...incomingOp };

    // Apply transformations for each conflicting operation
    for (const conflictingOp of conflictingOps) {
      transformedOp = this.transformAgainstOperation(transformedOp, conflictingOp);
    }

    return transformedOp;
  }

  private transformAgainstOperation(op: Operation, against: Operation): Operation {
    // Handle different operation type combinations
    switch (`${op.type}:${against.type}`) {
      case 'update:update':
        return this.transformUpdateUpdate(op, against);
      case 'update:delete':
        return this.transformUpdateDelete(op, against);
      case 'delete:update':
        return this.transformDeleteUpdate(op, against);
      case 'transform:transform':
        return this.transformTransformTransform(op, against);
      case 'create:create':
        return this.transformCreateCreate(op, against);
      default:
        return op; // No transformation needed
    }
  }

  private transformUpdateUpdate(op: Operation, against: Operation): Operation {
    // When two update operations conflict, merge the properties
    // Later timestamp wins for conflicting properties
    const mergedData = { ...against.data };
    
    // Apply op's changes, but only for properties not modified by 'against'
    Object.keys(op.data).forEach(key => {
      if (!(key in against.data) || op.timestamp > against.timestamp) {
        mergedData[key] = op.data[key];
      }
    });

    return {
      ...op,
      data: mergedData,
      dependencies: [...(op.dependencies || []), against.id],
    };
  }

  private transformUpdateDelete(op: Operation, against: Operation): Operation {
    // If object was deleted, convert update to no-op
    if (against.type === 'delete') {
      return {
        ...op,
        type: 'noop' as any,
        data: null,
        dependencies: [...(op.dependencies || []), against.id],
      };
    }
    return op;
  }

  private transformDeleteUpdate(op: Operation, against: Operation): Operation {
    // Delete takes precedence over update
    return {
      ...op,
      dependencies: [...(op.dependencies || []), against.id],
    };
  }

  private transformTransformTransform(op: Operation, against: Operation): Operation {
    // Transform operations (move, scale, rotate) need to be composed
    const transform1 = against.data.transform || {};
    const transform2 = op.data.transform || {};

    // Compose transformations
    const composedTransform = this.composeTransforms(transform1, transform2);

    return {
      ...op,
      data: {
        ...op.data,
        transform: composedTransform,
      },
      dependencies: [...(op.dependencies || []), against.id],
    };
  }

  private transformCreateCreate(op: Operation, against: Operation): Operation {
    // Handle concurrent creation of objects at same position
    if (op.data.x === against.data.x && op.data.y === against.data.y) {
      // Offset the position slightly to avoid overlap
      return {
        ...op,
        data: {
          ...op.data,
          x: op.data.x + 10,
          y: op.data.y + 10,
        },
        dependencies: [...(op.dependencies || []), against.id],
      };
    }
    return op;
  }

  private composeTransforms(t1: any, t2: any): any {
    // Compose two transformation matrices
    return {
      x: (t1.x || 0) + (t2.x || 0),
      y: (t1.y || 0) + (t2.y || 0),
      scaleX: (t1.scaleX || 1) * (t2.scaleX || 1),
      scaleY: (t1.scaleY || 1) * (t2.scaleY || 1),
      rotation: (t1.rotation || 0) + (t2.rotation || 0),
      skewX: (t1.skewX || 0) + (t2.skewX || 0),
      skewY: (t1.skewY || 0) + (t2.skewY || 0),
    };
  }

  // Check if an operation can be applied given the current state
  canApplyOperation(op: Operation, currentState: any): boolean {
    // Check dependencies are satisfied
    if (op.dependencies) {
      for (const depId of op.dependencies) {
        if (!this.operationHistory.has(depId)) {
          return false; // Dependency not yet applied
        }
      }
    }

    // Check object exists for update/delete operations
    if ((op.type === 'update' || op.type === 'delete') && !currentState.objects[op.objectId]) {
      return false;
    }

    // Check object doesn't exist for create operations
    if (op.type === 'create' && currentState.objects[op.objectId]) {
      return false;
    }

    return true;
  }

  // Apply operation to state
  applyOperation(op: Operation, currentState: any): any {
    const newState = { ...currentState };
    
    switch (op.type) {
      case 'create':
        newState.objects[op.objectId] = op.data;
        break;
      
      case 'update':
        if (newState.objects[op.objectId]) {
          newState.objects[op.objectId] = {
            ...newState.objects[op.objectId],
            ...op.data,
          };
        }
        break;
      
      case 'delete':
        delete newState.objects[op.objectId];
        break;
      
      case 'transform':
        if (newState.objects[op.objectId]) {
          const obj = newState.objects[op.objectId];
          const transform = op.data.transform;
          
          newState.objects[op.objectId] = {
            ...obj,
            x: obj.x + (transform.x || 0),
            y: obj.y + (transform.y || 0),
            scaleX: obj.scaleX * (transform.scaleX || 1),
            scaleY: obj.scaleY * (transform.scaleY || 1),
            rotation: obj.rotation + (transform.rotation || 0),
          };
        }
        break;
    }

    // Store operation in history
    this.operationHistory.set(op.id, op);
    
    return newState;
  }
}
```

This implementation provides a solid foundation for the core functionality of a Figma-like application with real-time collaboration, operational transform conflict resolution, and mobile-optimized vector graphics editing.