const ARROW_MAP = { up: '\u2191', down: '\u2193', left: '\u2190', right: '\u2192' };
const DEFAULT_IMAGE = '/static/img/default.png';

const state = {
    size: 3,
    tiles: [],
    imageUrl: DEFAULT_IMAGE,
    swapFirst: null,
    solving: false,
    animating: false,
    animationSpeed: 350,
    precision: 50,
    heuristic: 'manhattan',
    animTimer: null,
    solveTimeout: null,
};

function generateGoal(size) {
    const tiles = [];
    for (let i = 1; i < size * size; i++) tiles.push(i);
    tiles.push(0);
    return tiles;
}

function findBlank(tiles) {
    return tiles.indexOf(0);
}

function isAdjacent(pos1, pos2, size) {
    const r1 = Math.floor(pos1 / size), c1 = pos1 % size;
    const r2 = Math.floor(pos2 / size), c2 = pos2 % size;
    return Math.abs(r1 - r2) + Math.abs(c1 - c2) === 1;
}

function getGoalPosition(value, size) {
    if (value === 0) return size * size - 1;
    return value - 1;
}

function getPuzzlePixelSize() {
    const area = document.getElementById('puzzle-area');
    const availW = area.clientWidth - 32;
    const availH = area.clientHeight - 32;
    return Math.max(150, Math.min(availW, availH));
}

function init() {
    state.tiles = generateGoal(state.size);
    setupEventListeners();
    randomize();
    observeResize();
}

function observeResize() {
    const area = document.getElementById('puzzle-area');
    const ro = new ResizeObserver(() => renderPuzzle());
    ro.observe(area);
}

function setupEventListeners() {
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.size = parseInt(btn.dataset.size);
            state.tiles = generateGoal(state.size);
            randomize();
        });
    });

    document.querySelectorAll('.heuristic-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.heuristic-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.heuristic = btn.dataset.heuristic;
        });
    });

    document.getElementById('precision-slider').addEventListener('input', e => {
        state.precision = parseInt(e.target.value);
    });

    document.getElementById('speed-slider').addEventListener('input', e => {
        state.animationSpeed = parseInt(e.target.value);
    });

    document.getElementById('upload-btn').addEventListener('click', () => {
        document.getElementById('image-input').click();
    });

    document.getElementById('image-input').addEventListener('change', handleImageUpload);

    document.getElementById('randomize-btn').addEventListener('click', randomize);

    document.getElementById('resolve-btn').addEventListener('click', handleResolveClick);

    document.getElementById('crop-confirm').addEventListener('click', confirmCrop);
    document.getElementById('crop-cancel').addEventListener('click', cancelCrop);

    document.addEventListener('keydown', handleKeyboard);
}

function handleKeyboard(e) {
    if (state.animating || state.solving) return;
    const blank = findBlank(state.tiles);
    const size = state.size;
    const r = Math.floor(blank / size), c = blank % size;
    let targetPos = -1;

    switch (e.key) {
        case 'ArrowUp':    if (r < size - 1) targetPos = blank + size; break;
        case 'ArrowDown':  if (r > 0) targetPos = blank - size; break;
        case 'ArrowLeft':  if (c < size - 1) targetPos = blank + 1; break;
        case 'ArrowRight': if (c > 0) targetPos = blank - 1; break;
        default: return;
    }
    if (targetPos >= 0) {
        e.preventDefault();
        const newTiles = [...state.tiles];
        [newTiles[blank], newTiles[targetPos]] = [newTiles[targetPos], newTiles[blank]];
        state.tiles = newTiles;
        renderPuzzle();
    }
}

function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
        openCropModal(ev.target.result);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
}

let cropper = null;

function openCropModal(dataUrl) {
    const modal = document.getElementById('crop-modal');
    const img = document.getElementById('crop-image');
    modal.classList.remove('hidden');
    img.src = dataUrl;

    if (cropper) cropper.destroy();
    cropper = new Cropper(img, {
        aspectRatio: 1,
        viewMode: 1,
        autoCropArea: 1.0,
        background: false,
    });
}

function confirmCrop() {
    if (!cropper) return;
    const canvas = cropper.getCroppedCanvas({ aspectRatio: 1 });
    state.imageUrl = canvas.toDataURL('image/png');
    cancelCrop();
    renderPuzzle();
}

function cancelCrop() {
    const modal = document.getElementById('crop-modal');
    modal.classList.add('hidden');
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
}

async function randomize() {
    try {
        setStatus('');
        const res = await fetch('/api/randomize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size: state.size }),
        });
        const data = await res.json();
        if (data.error) {
            setStatus(data.error, 'error');
            return;
        }
        state.tiles = data.tiles;
        clearMoves();
        renderPuzzle();
    } catch (err) {
        setStatus('Error randomizing', 'error');
    }
}

function handleTileClick(index) {
    if (state.animating || state.solving) return;

    const blank = findBlank(state.tiles);

    if (isAdjacent(index, blank, state.size)) {
        state.swapFirst = null;
        const newTiles = [...state.tiles];
        [newTiles[blank], newTiles[index]] = [newTiles[index], newTiles[blank]];
        state.tiles = newTiles;
        clearMoves();
        renderPuzzle();
        return;
    }

    if (state.swapFirst === null) {
        state.swapFirst = index;
        renderPuzzle();
    } else if (state.swapFirst === index) {
        state.swapFirst = null;
        renderPuzzle();
    } else {
        const newTiles = [...state.tiles];
        [newTiles[state.swapFirst], newTiles[index]] = [newTiles[index], newTiles[state.swapFirst]];
        state.tiles = newTiles;
        state.swapFirst = null;
        clearMoves();
        renderPuzzle();
    }
}

function handleResolveClick() {
    if (state.animating) {
        cancelAnimation();
    } else {
        resolve();
    }
}

function cancelAnimation() {
    if (state.animTimer) {
        clearTimeout(state.animTimer);
        state.animTimer = null;
    }
    if (state.solveTimeout) {
        clearTimeout(state.solveTimeout);
        state.solveTimeout = null;
    }
    state.animating = false;
    state.solving = false;
    disableControls(false);
    setResolveButtonMode('resolve');
    setStatus('Solving cancelled', 'error');
}

function setResolveButtonMode(mode) {
    const btn = document.getElementById('resolve-btn');
    if (mode === 'cancel') {
        btn.textContent = 'Cancel';
        btn.className = 'btn btn-secondary';
    } else {
        btn.textContent = 'Resolve';
        btn.className = 'btn btn-accent';
    }
}

async function resolve() {
    if (state.solving || state.animating) return;

    const goal = generateGoal(state.size);
    if (arraysEqual(state.tiles, goal)) {
        setStatus('The puzzle is already solved!', 'success');
        return;
    }

    state.solving = true;
    showLoader(true);
    setStatus('Solving...');
    disableControls(true);

    state.solveTimeout = setTimeout(() => {
        if (state.solving && !state.animating) {
            state.solving = false;
            showLoader(false);
            disableControls(false);
            setStatus('Solving aborted after 30 seconds', 'error');
        }
    }, 30000);

    try {
        const res = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                size: state.size,
                tiles: state.tiles,
                precision: state.precision,
                heuristic: state.heuristic,
            }),
        });
        const data = await res.json();

        if (data.error) {
            setStatus(data.error, 'error');
            showLoader(false);
            state.solving = false;
            disableControls(false);
            return;
        }

        showLoader(false);
        setStatus(`Solved in ${data.stats.moves} moves (${data.time}s) - ${data.heuristic}`, 'success');
        animateSolution(data.path, data.moves);
    } catch (err) {
        setStatus('Error solving: ' + err.message, 'error');
        showLoader(false);
        state.solving = false;
        disableControls(false);
    }
}

function animateSolution(path, moves) {
    state.animating = true;
    disableControls(true);
    setResolveButtonMode('cancel');
    renderMoves(moves, -1);

    let step = 0;
    const totalSteps = path.length;

    function nextStep() {
        if (step >= totalSteps) {
            state.animating = false;
            state.solving = false;
            if (state.solveTimeout) {
                clearTimeout(state.solveTimeout);
                state.solveTimeout = null;
            }
            disableControls(false);
            setResolveButtonMode('resolve');
            renderMoves(moves, moves.length - 1);
            return;
        }
        state.tiles = path[step];
        renderPuzzle();
        renderMoves(moves, step - 1);
        step++;
        state.animTimer = setTimeout(nextStep, state.animationSpeed);
    }

    state.animTimer = setTimeout(nextStep, 200);
}

function renderPuzzle() {
    const grid = document.getElementById('puzzle-grid');
    const size = state.size;
    const pixelSize = getPuzzlePixelSize();
    const gap = 2;
    const border = 6;
    const tileSize = Math.floor((pixelSize - border - (size - 1) * gap) / size);
    const totalSize = tileSize * size + (size - 1) * gap;

    grid.style.width = totalSize + 'px';
    grid.style.height = totalSize + 'px';
    grid.style.gridTemplateColumns = `repeat(${size}, ${tileSize}px)`;
    grid.style.gridTemplateRows = `repeat(${size}, ${tileSize}px)`;

    const speedControl = document.getElementById('speed-control');
    speedControl.style.width = (totalSize + border) + 'px';

    grid.innerHTML = '';

    for (let i = 0; i < size * size; i++) {
        const value = state.tiles[i];
        const tile = document.createElement('div');
        tile.className = 'puzzle-tile';
        tile.dataset.index = i;

        if (value === 0) {
            tile.classList.add('blank');
        } else {
            const goalPos = getGoalPosition(value, size);
            const goalRow = Math.floor(goalPos / size);
            const goalCol = goalPos % size;

            tile.style.backgroundImage = `url(${state.imageUrl})`;
            tile.style.backgroundSize = `${size * 100}% ${size * 100}%`;

            if (size > 1) {
                const bgX = goalCol / (size - 1) * 100;
                const bgY = goalRow / (size - 1) * 100;
                tile.style.backgroundPosition = `${bgX}% ${bgY}%`;
            }

            const numSpan = document.createElement('span');
            numSpan.className = 'tile-number';
            numSpan.textContent = value;
            tile.appendChild(numSpan);
        }

        if (state.swapFirst === i) {
            tile.classList.add('selected');
        }

        tile.addEventListener('click', () => handleTileClick(i));
        grid.appendChild(tile);
    }
}

function renderMoves(moves, currentStep) {
    const container = document.getElementById('moves-content');
    container.innerHTML = '';

    moves.forEach((move, i) => {
        const span = document.createElement('span');
        span.className = 'move-arrow';
        if (i <= currentStep) span.classList.add('current');
        span.textContent = ARROW_MAP[move] || '?';
        span.title = `Step ${i + 1}: ${move}`;
        container.appendChild(span);
    });

    if (currentStep >= 0) {
        const currentEl = container.children[currentStep];
        if (currentEl) {
            currentEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    }
}

function clearMoves() {
    document.getElementById('moves-content').innerHTML = '';
}

function showLoader(show) {
    document.getElementById('puzzle-loader').classList.toggle('hidden', !show);
}

function disableControls(disabled) {
    document.getElementById('randomize-btn').disabled = disabled;
    document.getElementById('upload-btn').disabled = disabled;
    document.querySelectorAll('.size-btn').forEach(b => b.disabled = disabled);
}

function setStatus(msg, type = '') {
    const el = document.getElementById('status-msg');
    el.textContent = msg;
    el.className = 'status-msg' + (type ? ' ' + type : '') + (msg ? ' visible' : '');
}

function arraysEqual(a, b) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) return false;
    }
    return true;
}

document.addEventListener('DOMContentLoaded', init);
