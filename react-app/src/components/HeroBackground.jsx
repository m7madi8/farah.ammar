/**
 * HeroBackground — WebGL animated gradient background for the hero section.
 * Uses raw WebGL (no OGL dependency). Full-screen quad + fragment shader.
 */

import { useEffect, useRef } from 'react';

const vertexSrc = `
  attribute vec2 position;
  void main() {
    gl_Position = vec4(position, 0.0, 1.0);
  }
`;

const fragmentSrc = `
  precision highp float;
  uniform float uTime;
  uniform vec2 uResolution;

  void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;
    float t = uTime * 0.6;
    float angle = 0.4 + sin(t) * 0.25;
    float s = uv.x * cos(angle) + uv.y * sin(angle);
    s = s * 0.5 + 0.5;
    s = s + sin(uTime * 0.4) * 0.08;

    vec3 c1 = vec3(0.176, 0.102, 0.239);
    vec3 c2 = vec3(0.294, 0.165, 0.388);
    vec3 c3 = vec3(0.478, 0.361, 0.557);
    vec3 c4 = vec3(0.239, 0.133, 0.310);

    float darkEnd = 0.70;
    vec3 col = mix(c1, c2, smoothstep(0.0, 0.35, s));
    col = mix(col, c4, smoothstep(0.35, darkEnd, s));
    col = mix(col, c3, smoothstep(darkEnd, 1.0, s));

    float glow = 1.0 - length(uv - vec2(0.5, 0.85));
    glow = smoothstep(0.0, 0.5, glow) * (0.08 + 0.06 * sin(uTime * 1.2));
    col += vec3(0.95, 0.89, 0.88) * glow;

    float glow2 = 1.0 - length(uv - vec2(0.75 + sin(uTime * 0.5) * 0.1, 0.15));
    glow2 = smoothstep(0.0, 0.45, glow2) * (0.08 + 0.06 * sin(uTime * 0.8));
    col += vec3(0.478, 0.361, 0.557) * glow2;

    gl_FragColor = vec4(col, 1.0);
  }
`;

function compileShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

function createProgram(gl, vertSrc, fragSrc) {
  const vert = compileShader(gl, gl.VERTEX_SHADER, vertSrc);
  const frag = compileShader(gl, gl.FRAGMENT_SHADER, fragSrc);
  if (!vert || !frag) return null;
  const program = gl.createProgram();
  gl.attachShader(program, vert);
  gl.attachShader(program, frag);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    gl.deleteProgram(program);
    return null;
  }
  return program;
}

// Full-screen quad (two triangles)
const QUAD = new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]);

export function HeroBackground() {
  const containerRef = useRef(null);
  const rafRef = useRef(null);
  const startTimeRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const canvas = document.createElement('canvas');
    canvas.className = 'hero-ogl-canvas';
    container.appendChild(canvas);

    const gl = canvas.getContext('webgl', { alpha: false, antialias: true });
    if (!gl) return;

    const program = createProgram(gl, vertexSrc, fragmentSrc);
    if (!program) return;

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, QUAD, gl.STATIC_DRAW);

    const positionLoc = gl.getAttribLocation(program, 'position');
    const uTime = gl.getUniformLocation(program, 'uTime');
    const uResolution = gl.getUniformLocation(program, 'uResolution');

    const resize = () => {
      if (!container.parentElement) return;
      const w = container.offsetWidth;
      const h = container.offsetHeight;
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      gl.viewport(0, 0, canvas.width, canvas.height);
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
    resize();

    startTimeRef.current = performance.now() / 1000;

    const animate = () => {
      rafRef.current = requestAnimationFrame(animate);
      if (!container.parentElement) return;
      const time = performance.now() / 1000 - startTimeRef.current;
      gl.clearColor(0.176, 0.102, 0.239, 1.0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(program);
      gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.enableVertexAttribArray(positionLoc);
      gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);
      gl.uniform1f(uTime, time);
      gl.uniform2f(uResolution, canvas.width, canvas.height);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    };
    animate();

    return () => {
      rafRef.current && cancelAnimationFrame(rafRef.current);
      resizeObserver.disconnect();
      if (canvas.parentNode) container.removeChild(canvas);
    };
  }, []);

  return <div ref={containerRef} className="hero-bg-ogl" aria-hidden="true" />;
}
