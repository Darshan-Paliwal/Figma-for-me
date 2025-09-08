// DesignStudio - Mobile-First Design Collaboration Application

class DesignStudioApp {
    constructor() {
        this.currentTool = 'select';
        this.selectedObject = null;
        this.isDrawing = false;
        this.drawingPath = null;
        this.zoomLevel = 1;
        this.panOffset = { x: 0, y: 0 };
        this.activeMobilePanel = 'tools';
        
        // Application data from JSON
        this.data = {
            projects: [
                {
                    id: "project-1",
                    name: "Mobile App Design",
                    artboards: [
                        {
                            id: "artboard-1",
                            name: "Home Screen",
                            width: 375,
                            height: 812,
                            objects: []
                        }
                    ]
                }
            ],
            tools: [
                {"id": "select", "name": "Selection", "icon": "cursor", "shortcut": "V"},
                {"id": "pen", "name": "Pen Tool", "icon": "edit", "shortcut": "P"},
                {"id": "rectangle", "name": "Rectangle", "icon": "square", "shortcut": "R"},
                {"id": "circle", "name": "Circle", "icon": "circle", "shortcut": "O"},
                {"id": "text", "name": "Text", "icon": "type", "shortcut": "T"},
                {"id": "line", "name": "Line", "icon": "minus", "shortcut": "L"}
            ],
            users: [
                {
                    id: "user-1",
                    name: "Alex Chen",
                    avatar: "#FF6B6B",
                    cursor: {"x": 250, "y": 180},
                    isOnline: true
                },
                {
                    id: "user-2", 
                    name: "Sarah Kim",
                    avatar: "#4ECDC4",
                    cursor: {"x": 320, "y": 240},
                    isOnline: true
                }
            ],
            layers: [
                {
                    id: "layer-1",
                    name: "Background",
                    type: "rectangle",
                    visible: true,
                    locked: false,
                    properties: {
                        x: 0,
                        y: 0,
                        width: 375,
                        height: 812,
                        fill: "#F8F9FA",
                        stroke: "none"
                    }
                }
            ],
            comments: [
                {
                    id: "comment-1",
                    x: 200,
                    y: 150,
                    author: "Sarah Kim",
                    text: "Consider making this button larger for better accessibility",
                    timestamp: "2025-09-08T08:15:00Z",
                    resolved: false
                }
            ],
            colorPalette: [
                "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3", "#54A0FF", "#5F27CD"
            ],
            exportFormats: [
                {"id": "png", "name": "PNG", "extension": ".png"},
                {"id": "svg", "name": "SVG", "extension": ".svg"},
                {"id": "pdf", "name": "PDF", "extension": ".pdf"},
                {"id": "jpg", "name": "JPEG", "extension": ".jpg"}
            ]
        };

        this.objects = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.renderLayers();
        this.renderComments();
        this.renderColorPalette();
        this.startCollaborationSimulation();
        this.setupKeyboardShortcuts();
        this.setupCanvasInteractions();
        this.setupModalHandlers();
        
        // Ensure all modals start hidden
        this.hideAllModals();
        
        // Initialize with landing page
        this.showLandingPage();
    }

    setupEventListeners() {
        // Tool selection
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.currentTarget.dataset.tool;
                this.selectTool(tool);
            });
        });

        // Bottom toolbar navigation
        document.querySelectorAll('.bottom-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const panel = e.currentTarget.dataset.panel;
                this.showMobilePanel(panel);
            });
        });

        // Canvas events
        const canvas = document.getElementById('main-canvas');
        canvas.addEventListener('mousedown', this.onCanvasMouseDown.bind(this));
        canvas.addEventListener('mousemove', this.onCanvasMouseMove.bind(this));
        canvas.addEventListener('mouseup', this.onCanvasMouseUp.bind(this));
        canvas.addEventListener('click', this.onCanvasClick.bind(this));

        // Touch events for mobile
        canvas.addEventListener('touchstart', this.onCanvasTouchStart.bind(this));
        canvas.addEventListener('touchmove', this.onCanvasTouchMove.bind(this));
        canvas.addEventListener('touchend', this.onCanvasTouchEnd.bind(this));

        // Window resize
        window.addEventListener('resize', this.onWindowResize.bind(this));
    }

    setupModalHandlers() {
        // Setup escape key handler for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeActiveModal();
            }
        });

        // Setup backdrop click handlers
        document.querySelectorAll('.modal').forEach(modal => {
            const backdrop = modal.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.addEventListener('click', (e) => {
                    if (e.target === backdrop) {
                        this.closeModal(modal.id);
                    }
                });
            }
        });

        // Setup close button handlers
        document.querySelectorAll('.modal-close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    closeActiveModal() {
        const activeModal = document.querySelector('.modal:not(.hidden)');
        if (activeModal) {
            this.closeModal(activeModal.id);
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            // Don't handle shortcuts when modals are open
            if (document.querySelector('.modal:not(.hidden)')) return;
            
            switch(e.key.toLowerCase()) {
                case 'v': this.selectTool('select'); break;
                case 'p': this.selectTool('pen'); break;
                case 'r': this.selectTool('rectangle'); break;
                case 'o': this.selectTool('circle'); break;
                case 't': this.selectTool('text'); break;
                case 'l': this.selectTool('line'); break;
                case 'delete':
                case 'backspace':
                    if (this.selectedObject) {
                        this.deleteSelectedObject();
                    }
                    break;
                case 'z':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        if (e.shiftKey) {
                            this.redo();
                        } else {
                            this.undo();
                        }
                    }
                    break;
            }
        });
    }

    setupCanvasInteractions() {
        const canvasWrapper = document.getElementById('canvas-wrapper');
        let isDragging = false;
        let lastPoint = null;

        // Pan functionality
        canvasWrapper.addEventListener('mousedown', (e) => {
            if (this.currentTool === 'select' && e.target === canvasWrapper) {
                isDragging = true;
                lastPoint = { x: e.clientX, y: e.clientY };
                canvasWrapper.style.cursor = 'grabbing';
            }
        });

        canvasWrapper.addEventListener('mousemove', (e) => {
            if (isDragging && lastPoint) {
                const deltaX = e.clientX - lastPoint.x;
                const deltaY = e.clientY - lastPoint.y;
                canvasWrapper.scrollLeft -= deltaX;
                canvasWrapper.scrollTop -= deltaY;
                lastPoint = { x: e.clientX, y: e.clientY };
            }
        });

        canvasWrapper.addEventListener('mouseup', () => {
            isDragging = false;
            canvasWrapper.style.cursor = '';
        });

        // Zoom functionality
        canvasWrapper.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            this.zoomLevel *= delta;
            this.zoomLevel = Math.max(0.1, Math.min(5, this.zoomLevel));
            this.updateZoom();
        });
    }

    // Landing page and navigation
    showLandingPage() {
        document.getElementById('landing-page').classList.remove('hidden');
        document.getElementById('app-interface').classList.add('hidden');
    }

    startNewProject() {
        document.getElementById('landing-page').classList.add('hidden');
        document.getElementById('app-interface').classList.remove('hidden');
        this.selectTool('select');
        this.showMobilePanel('tools');
    }

    showProjects() {
        // Simulate showing recent projects
        this.showNotification('Recent projects feature coming soon!', 'info');
    }

    goToLanding() {
        this.showLandingPage();
    }

    // Tool management
    selectTool(toolId) {
        this.currentTool = toolId;
        
        // Update UI
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const toolBtn = document.querySelector(`[data-tool="${toolId}"]`);
        if (toolBtn) {
            toolBtn.classList.add('active');
        }

        // Update cursor
        const canvas = document.getElementById('main-canvas');
        switch(toolId) {
            case 'select':
                canvas.style.cursor = 'default';
                break;
            case 'pen':
                canvas.style.cursor = 'crosshair';
                break;
            case 'text':
                canvas.style.cursor = 'text';
                break;
            default:
                canvas.style.cursor = 'crosshair';
        }
    }

    // Canvas drawing events
    onCanvasMouseDown(e) {
        if (this.currentTool === 'select') return;
        
        const point = this.getCanvasPoint(e);
        this.isDrawing = true;
        this.startDrawing(point);
    }

    onCanvasMouseMove(e) {
        if (!this.isDrawing) return;
        
        const point = this.getCanvasPoint(e);
        this.updateDrawing(point);
    }

    onCanvasMouseUp(e) {
        if (!this.isDrawing) return;
        
        const point = this.getCanvasPoint(e);
        this.finishDrawing(point);
        this.isDrawing = false;
    }

    onCanvasClick(e) {
        if (this.currentTool === 'select') {
            const point = this.getCanvasPoint(e);
            const clickedObject = this.getObjectAtPoint(point);
            this.selectObject(clickedObject);
        }
    }

    // Touch events
    onCanvasTouchStart(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.onCanvasMouseDown(mouseEvent);
        }
    }

    onCanvasTouchMove(e) {
        e.preventDefault();
        if (e.touches.length === 1 && this.isDrawing) {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.onCanvasMouseMove(mouseEvent);
        }
    }

    onCanvasTouchEnd(e) {
        e.preventDefault();
        if (this.isDrawing) {
            this.onCanvasMouseUp(e);
        }
    }

    getCanvasPoint(e) {
        const canvas = document.getElementById('main-canvas');
        const rect = canvas.getBoundingClientRect();
        const scaleX = 375 / rect.width;
        const scaleY = 812 / rect.height;
        
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }

    // Drawing operations
    startDrawing(point) {
        const id = 'obj-' + Date.now();
        
        switch(this.currentTool) {
            case 'rectangle':
                this.drawingPath = {
                    id,
                    type: 'rectangle',
                    startX: point.x,
                    startY: point.y,
                    x: point.x,
                    y: point.y,
                    width: 0,
                    height: 0,
                    fill: '#4ECDC4',
                    stroke: '#333',
                    strokeWidth: 2
                };
                this.createSVGElement(this.drawingPath);
                break;
            case 'circle':
                this.drawingPath = {
                    id,
                    type: 'circle',
                    startX: point.x,
                    startY: point.y,
                    cx: point.x,
                    cy: point.y,
                    r: 0,
                    fill: '#FF6B6B',
                    stroke: '#333',
                    strokeWidth: 2
                };
                this.createSVGElement(this.drawingPath);
                break;
            case 'line':
                this.drawingPath = {
                    id,
                    type: 'line',
                    x1: point.x,
                    y1: point.y,
                    x2: point.x,
                    y2: point.y,
                    stroke: '#333',
                    strokeWidth: 2
                };
                this.createSVGElement(this.drawingPath);
                break;
        }
    }

    updateDrawing(point) {
        if (!this.drawingPath) return;

        switch(this.drawingPath.type) {
            case 'rectangle':
                this.drawingPath.width = Math.abs(point.x - this.drawingPath.startX);
                this.drawingPath.height = Math.abs(point.y - this.drawingPath.startY);
                this.drawingPath.x = Math.min(point.x, this.drawingPath.startX);
                this.drawingPath.y = Math.min(point.y, this.drawingPath.startY);
                break;
            case 'circle':
                const dx = point.x - this.drawingPath.startX;
                const dy = point.y - this.drawingPath.startY;
                this.drawingPath.r = Math.sqrt(dx * dx + dy * dy);
                break;
            case 'line':
                this.drawingPath.x2 = point.x;
                this.drawingPath.y2 = point.y;
                break;
        }

        this.updateSVGElement(this.drawingPath);
    }

    finishDrawing(point) {
        if (this.drawingPath) {
            // Only add if it has meaningful size
            let shouldAdd = false;
            switch(this.drawingPath.type) {
                case 'rectangle':
                    shouldAdd = this.drawingPath.width > 5 && this.drawingPath.height > 5;
                    break;
                case 'circle':
                    shouldAdd = this.drawingPath.r > 5;
                    break;
                case 'line':
                    const dx = this.drawingPath.x2 - this.drawingPath.x1;
                    const dy = this.drawingPath.y2 - this.drawingPath.y1;
                    shouldAdd = Math.sqrt(dx * dx + dy * dy) > 5;
                    break;
            }

            if (shouldAdd) {
                // Add to objects array
                this.objects.push({ ...this.drawingPath });
                
                // Add to layers
                this.data.layers.push({
                    id: this.drawingPath.id,
                    name: `${this.drawingPath.type} ${this.objects.length}`,
                    type: this.drawingPath.type,
                    visible: true,
                    locked: false,
                    properties: { ...this.drawingPath }
                });

                this.renderLayers();
                this.selectTool('select');
                this.showNotification(`${this.drawingPath.type} created!`, 'success');
            } else {
                // Remove the element if too small
                const element = document.getElementById(this.drawingPath.id);
                if (element) {
                    element.remove();
                }
            }

            this.drawingPath = null;
        }
    }

    createSVGElement(obj) {
        const canvas = document.getElementById('main-canvas');
        let element;

        switch(obj.type) {
            case 'rectangle':
                element = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                element.setAttribute('id', obj.id);
                element.setAttribute('class', 'canvas-object');
                break;
            case 'circle':
                element = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                element.setAttribute('id', obj.id);
                element.setAttribute('class', 'canvas-object');
                break;
            case 'line':
                element = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                element.setAttribute('id', obj.id);
                element.setAttribute('class', 'canvas-object');
                break;
        }

        if (element) {
            canvas.appendChild(element);
            this.updateSVGElement(obj);
        }
    }

    updateSVGElement(obj) {
        const element = document.getElementById(obj.id);
        if (!element) return;

        switch(obj.type) {
            case 'rectangle':
                element.setAttribute('x', obj.x);
                element.setAttribute('y', obj.y);
                element.setAttribute('width', obj.width);
                element.setAttribute('height', obj.height);
                element.setAttribute('fill', obj.fill || 'transparent');
                element.setAttribute('stroke', obj.stroke || 'black');
                element.setAttribute('stroke-width', obj.strokeWidth || 1);
                break;
            case 'circle':
                element.setAttribute('cx', obj.cx);
                element.setAttribute('cy', obj.cy);
                element.setAttribute('r', obj.r);
                element.setAttribute('fill', obj.fill || 'transparent');
                element.setAttribute('stroke', obj.stroke || 'black');
                element.setAttribute('stroke-width', obj.strokeWidth || 1);
                break;
            case 'line':
                element.setAttribute('x1', obj.x1);
                element.setAttribute('y1', obj.y1);
                element.setAttribute('x2', obj.x2);
                element.setAttribute('y2', obj.y2);
                element.setAttribute('stroke', obj.stroke || 'black');
                element.setAttribute('stroke-width', obj.strokeWidth || 1);
                break;
        }
    }

    getObjectAtPoint(point) {
        // Simple hit testing - in a real app this would be more sophisticated
        for (let obj of this.objects) {
            if (this.isPointInObject(point, obj)) {
                return obj;
            }
        }
        return null;
    }

    isPointInObject(point, obj) {
        switch(obj.type) {
            case 'rectangle':
                return point.x >= obj.x && point.x <= obj.x + obj.width &&
                       point.y >= obj.y && point.y <= obj.y + obj.height;
            case 'circle':
                const dx = point.x - obj.cx;
                const dy = point.y - obj.cy;
                return Math.sqrt(dx * dx + dy * dy) <= obj.r;
            default:
                return false;
        }
    }

    selectObject(obj) {
        this.selectedObject = obj;
        
        // Update layer selection
        document.querySelectorAll('.layer-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        if (obj) {
            const layerElement = document.querySelector(`[data-layer-id="${obj.id}"]`);
            if (layerElement) {
                layerElement.classList.add('selected');
            }
            this.showObjectProperties(obj);
            this.showMobilePanel('properties'); // Auto-switch to properties on mobile
        } else {
            this.showNoSelection();
        }
    }

    deleteSelectedObject() {
        if (!this.selectedObject) return;
        
        // Remove from DOM
        const element = document.getElementById(this.selectedObject.id);
        if (element) {
            element.remove();
        }
        
        // Remove from arrays
        this.objects = this.objects.filter(obj => obj.id !== this.selectedObject.id);
        this.data.layers = this.data.layers.filter(layer => layer.id !== this.selectedObject.id);
        
        this.selectedObject = null;
        this.renderLayers();
        this.showNoSelection();
        this.showNotification('Object deleted', 'info');
    }

    // UI Management
    showMobilePanel(panelId) {
        this.activeMobilePanel = panelId;
        
        // Hide all panels
        document.querySelectorAll('.left-panel, .right-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Update bottom tabs
        document.querySelectorAll('.bottom-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        const targetTab = document.querySelector(`[data-panel="${panelId}"]`);
        if (targetTab) {
            targetTab.classList.add('active');
        }
        
        // Show appropriate panel
        switch(panelId) {
            case 'tools':
            case 'layers':
            case 'comments':
                document.getElementById('left-panel').classList.add('active');
                break;
            case 'properties':
                document.getElementById('right-panel').classList.add('active');
                break;
        }
    }

    toggleMobileMenu() {
        const menu = document.getElementById('mobile-menu');
        menu.classList.toggle('hidden');
    }

    // Layer management
    renderLayers() {
        const layersList = document.getElementById('layers-list');
        layersList.innerHTML = '';
        
        [...this.data.layers].reverse().forEach(layer => {
            const layerElement = document.createElement('div');
            layerElement.className = 'layer-item';
            layerElement.dataset.layerId = layer.id;
            layerElement.innerHTML = `
                <button class="layer-visibility" onclick="app.toggleLayerVisibility('${layer.id}')">
                    ${layer.visible ? '👁' : '🙈'}
                </button>
                <div class="layer-icon" style="background-color: ${this.getLayerColor(layer.type)}">
                    ${this.getLayerIcon(layer.type)}
                </div>
                <span class="layer-name">${layer.name}</span>
            `;
            
            layerElement.addEventListener('click', () => {
                const obj = this.objects.find(o => o.id === layer.id);
                this.selectObject(obj);
            });
            
            layersList.appendChild(layerElement);
        });
    }

    getLayerIcon(type) {
        const icons = {
            rectangle: '▭',
            circle: '●',
            line: '—',
            text: 'T',
            pen: '✎'
        };
        return icons[type] || '?';
    }

    getLayerColor(type) {
        const colors = {
            rectangle: '#4ECDC4',
            circle: '#FF6B6B',
            line: '#45B7D1',
            text: '#96CEB4',
            pen: '#FECA57'
        };
        return colors[type] || '#999';
    }

    toggleLayerVisibility(layerId) {
        const layer = this.data.layers.find(l => l.id === layerId);
        if (layer) {
            layer.visible = !layer.visible;
            const element = document.getElementById(layerId);
            if (element) {
                element.style.display = layer.visible ? 'block' : 'none';
            }
            this.renderLayers();
        }
    }

    // Properties panel
    showObjectProperties(obj) {
        const propertiesContent = document.getElementById('properties-content');
        propertiesContent.innerHTML = `
            <div class="property-group">
                <div class="property-label">Position & Size</div>
                <div class="property-row">
                    <input type="number" class="form-control property-input" placeholder="X" value="${Math.round(obj.x || obj.cx || obj.x1 || 0)}" onchange="app.updateObjectProperty('x', this.value)">
                    <input type="number" class="form-control property-input" placeholder="Y" value="${Math.round(obj.y || obj.cy || obj.y1 || 0)}" onchange="app.updateObjectProperty('y', this.value)">
                </div>
                ${obj.type === 'rectangle' ? `
                <div class="property-row">
                    <input type="number" class="form-control property-input" placeholder="Width" value="${Math.round(obj.width || 0)}" onchange="app.updateObjectProperty('width', this.value)">
                    <input type="number" class="form-control property-input" placeholder="Height" value="${Math.round(obj.height || 0)}" onchange="app.updateObjectProperty('height', this.value)">
                </div>
                ` : ''}
                ${obj.type === 'circle' ? `
                <div class="property-row">
                    <input type="number" class="form-control property-input" placeholder="Radius" value="${Math.round(obj.r || 0)}" onchange="app.updateObjectProperty('r', this.value)">
                </div>
                ` : ''}
            </div>
            <div class="property-group">
                <div class="property-label">Appearance</div>
                <div class="property-row">
                    <label>Fill:</label>
                    <input type="color" class="form-control" value="${obj.fill || '#4ECDC4'}" onchange="app.updateObjectProperty('fill', this.value)">
                </div>
                <div class="property-row">
                    <label>Stroke:</label>
                    <input type="color" class="form-control" value="${obj.stroke || '#333'}" onchange="app.updateObjectProperty('stroke', this.value)">
                </div>
                <div class="property-row">
                    <label>Stroke Width:</label>
                    <input type="number" class="form-control" min="0" max="20" value="${obj.strokeWidth || 2}" onchange="app.updateObjectProperty('strokeWidth', this.value)">
                </div>
            </div>
        `;
    }

    showNoSelection() {
        const propertiesContent = document.getElementById('properties-content');
        propertiesContent.innerHTML = `
            <div class="no-selection">
                <p>Select an object to edit properties</p>
            </div>
        `;
    }

    updateObjectProperty(property, value) {
        if (!this.selectedObject) return;
        
        // Convert to appropriate type
        const numValue = parseFloat(value);
        const finalValue = isNaN(numValue) ? value : numValue;
        
        // Update object
        this.selectedObject[property] = finalValue;
        
        // Update in layers array
        const layer = this.data.layers.find(l => l.id === this.selectedObject.id);
        if (layer) {
            layer.properties[property] = finalValue;
        }
        
        // Update SVG element
        this.updateSVGElement(this.selectedObject);
    }

    // Comments
    renderComments() {
        const commentsList = document.getElementById('comments-list');
        commentsList.innerHTML = '';
        
        this.data.comments.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.className = 'comment-item';
            commentElement.innerHTML = `
                <div class="comment-author">${comment.author}</div>
                <div class="comment-text">${comment.text}</div>
                <div class="comment-time">${new Date(comment.timestamp).toLocaleDateString()}</div>
            `;
            commentsList.appendChild(commentElement);
        });
        
        // Render comment markers on canvas
        this.renderCommentMarkers();
    }

    renderCommentMarkers() {
        const markersContainer = document.getElementById('comment-markers');
        markersContainer.innerHTML = '';
        
        this.data.comments.forEach((comment, index) => {
            const marker = document.createElement('div');
            marker.className = 'comment-marker';
            marker.style.left = `${(comment.x / 375) * 100}%`;
            marker.style.top = `${(comment.y / 812) * 100}%`;
            marker.textContent = index + 1;
            marker.addEventListener('click', () => {
                this.showMobilePanel('comments');
            });
            markersContainer.appendChild(marker);
        });
    }

    // Color palette
    renderColorPalette() {
        const colorPalette = document.querySelector('.color-palette');
        colorPalette.innerHTML = '';
        
        this.data.colorPalette.forEach(color => {
            const swatch = document.createElement('div');
            swatch.className = 'color-swatch';
            swatch.style.backgroundColor = color;
            swatch.addEventListener('click', () => {
                this.selectColor(color);
            });
            colorPalette.appendChild(swatch);
        });
    }

    selectColor(color) {
        // Update active swatch
        document.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Apply to selected object if any
        if (this.selectedObject) {
            this.updateObjectProperty('fill', color);
            this.showObjectProperties(this.selectedObject);
        }
    }

    // Collaboration simulation
    startCollaborationSimulation() {
        const liveCursors = document.getElementById('live-cursors');
        
        this.data.users.forEach(user => {
            if (user.id === 'current-user') return;
            
            const cursor = document.createElement('div');
            cursor.className = 'live-cursor';
            cursor.style.color = user.avatar;
            cursor.innerHTML = `
                <svg class="cursor-icon" viewBox="0 0 24 24">
                    <path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/>
                </svg>
                <div class="cursor-label">${user.name}</div>
            `;
            liveCursors.appendChild(cursor);
            
            // Animate cursor movement
            this.animateCursor(cursor, user);
        });
    }

    animateCursor(cursorElement, user) {
        setInterval(() => {
            // Random movement simulation
            user.cursor.x += (Math.random() - 0.5) * 20;
            user.cursor.y += (Math.random() - 0.5) * 20;
            
            // Keep within bounds
            user.cursor.x = Math.max(0, Math.min(375, user.cursor.x));
            user.cursor.y = Math.max(0, Math.min(812, user.cursor.y));
            
            // Update position
            cursorElement.style.left = `${(user.cursor.x / 375) * 100}%`;
            cursorElement.style.top = `${(user.cursor.y / 812) * 100}%`;
        }, 2000 + Math.random() * 3000);
    }

    // Zoom and pan
    zoomIn() {
        this.zoomLevel = Math.min(5, this.zoomLevel * 1.2);
        this.updateZoom();
    }

    zoomOut() {
        this.zoomLevel = Math.max(0.1, this.zoomLevel / 1.2);
        this.updateZoom();
    }

    updateZoom() {
        const canvas = document.getElementById('main-canvas');
        canvas.style.transform = `scale(${this.zoomLevel})`;
        
        // Update zoom display
        const zoomDisplay = document.querySelector('.zoom-level');
        if (zoomDisplay) {
            zoomDisplay.textContent = Math.round(this.zoomLevel * 100) + '%';
        }
    }

    // History (simplified)
    undo() {
        this.showNotification('Undo action', 'info');
        // In a real app, this would restore previous state
    }

    redo() {
        this.showNotification('Redo action', 'info');
        // In a real app, this would restore next state
    }

    // Modal management
    showExportDialog() {
        const modal = document.getElementById('export-modal');
        modal.classList.remove('hidden');
    }

    showAnimationDialog() {
        const modal = document.getElementById('animation-modal');
        modal.classList.remove('hidden');
        this.toggleMobileMenu();
    }

    showSettingsDialog() {
        this.showNotification('Settings dialog coming soon!', 'info');
        this.toggleMobileMenu();
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    // Export functionality
    exportDesign() {
        const format = document.getElementById('export-format').value;
        const scale = document.getElementById('export-scale').value;
        const quality = document.getElementById('export-quality').value;
        
        // Simulate export
        const canvas = document.getElementById('main-canvas');
        const svgData = new XMLSerializer().serializeToString(canvas);
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `design.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        this.closeModal('export-modal');
        
        // Show success message
        this.showNotification('Design exported successfully!', 'success');
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            background: var(--color-${type === 'success' ? 'success' : 'primary'});
            box-shadow: var(--shadow-lg);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Window resize handler
    onWindowResize() {
        // Update canvas positioning and mobile panel states
        if (window.innerWidth >= 1024) {
            // Desktop mode - show all panels
            document.getElementById('left-panel').classList.add('active');
            document.getElementById('right-panel').classList.add('active');
        } else {
            // Mobile mode - show active panel only
            this.showMobilePanel(this.activeMobilePanel);
        }
    }
}

// Initialize the application
const app = new DesignStudioApp();

// Global functions for HTML onclick handlers
window.app = app;