import { useState, useEffect, useMemo, useRef } from 'react';
import type { FC } from 'react';
import { 
  Play, 
  Pause, 
  Activity, 
  AlertTriangle, 
  Footprints, 
  Heart, 
  Utensils, 
  ArrowUpRight, 
  ArrowDownRight, 
  ArrowRight,
  Check
} from 'lucide-react';

// --- DATA TYPES ---
export interface Point {
  x: number;
  y: number;
  val: number;
  idx: number;
  hr: number;
  iob: number;
  trend: 'rising' | 'falling' | 'stable';
}

export interface Space {
  x: number;
  y: number;
  w: number;
  h: number;
  area: number;
  type: 'above' | 'below';
}

// --- DATA GENERATION ---
const INITIAL_POINTS = 30;

const generateSyntheticPoints = (walkActive: boolean = false): number[] => {
  return Array.from({ length: INITIAL_POINTS }).map((_, i) => {
    const progress = i / (INITIAL_POINTS - 1);
    // Baseline circadian curve
    let val = 135 + Math.sin(progress * Math.PI * 2) * 45;
    
    // Simulate post-lunch spike around index 10-22
    if (i >= 10 && i <= 22) {
      const mealProgress = (i - 10) / 12;
      const spikePeak = walkActive ? 22 : 55; // Walk blunts spike significantly
      val += Math.sin(mealProgress * Math.PI) * spikePeak;
    }

    val += (Math.sin(i * 1.5) * 6) + (Math.random() * 6 - 3);
    return Math.max(60, Math.min(220, val));
  });
};

// --- SF-LG GREEDY SPACE ALLOCATION ALGORITHM ---
const calculateSpaces = (points: Point[]): Space[] => {
  // Bounding box strictly inside the 300x300 circle to prevent corner clipping
  const TOP_BOUND = 58; 
  const BOTTOM_BOUND = 242;
  const MIN_W = 38;
  const MIN_H = 36;

  const candidates: Space[] = [];

  // Iterate over all possible X-axis segments
  for (let i = 0; i < points.length; i++) {
    for (let j = i + 1; j < points.length; j++) {
      const pI = points[i];
      const pJ = points[j];
      if (!pI || !pJ) continue;

      const w = pJ.x - pI.x;
      if (w < MIN_W) continue;

      const slice = points.slice(i, j + 1);
      const minY = Math.min(...slice.map((p) => p.y)); 
      const maxY = Math.max(...slice.map((p) => p.y)); 

      // Candidate 1: Space Above the curve
      const hAbove = minY - TOP_BOUND;
      if (hAbove >= MIN_H) {
        candidates.push({ x: pI.x, y: TOP_BOUND, w, h: hAbove, area: w * hAbove, type: 'above' });
      }

      // Candidate 2: Space Below the curve
      const hBelow = BOTTOM_BOUND - maxY;
      if (hBelow >= MIN_H) {
        candidates.push({ x: pI.x, y: maxY, w, h: hBelow, area: w * hBelow, type: 'below' });
      }
    }
  }

  // Sort candidates by area descending
  candidates.sort((a, b) => b.area - a.area);

  // Greedy Allocation: Pick the largest non-overlapping rectangles
  const selected: Space[] = [];
  for (const cand of candidates) {
    const isOverlap = selected.some((s) => {
      return !(cand.x + cand.w <= s.x || s.x + s.w <= cand.x || cand.y + cand.h <= s.y || s.y + s.h <= cand.y);
    });

    if (!isOverlap) {
      selected.push(cand);
      if (selected.length >= 2) break; // Top 2 spaces
    }
  }

  return selected;
};

// --- MAIN COMPONENT ---
export default function App() {
  const [scenario, setScenario] = useState<number>(4); // Default to the exciting Spike & Walk feature
  const [walkActive, setWalkActive] = useState<boolean>(false);
  const [data, setData] = useState<number[]>(() => generateSyntheticPoints(false));
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [selectedPoints, setSelectedPoints] = useState<number[]>([]);
  const [notificationExpanded, setNotificationExpanded] = useState<boolean>(false);
  const tickRef = useRef<number>(0);

  // Circular Watch Dimensions
  const SIZE = 300; 
  const PAD_X = 38; 

  // Re-generate curve if walk status changes in Scenario 4
  useEffect(() => {
    if (scenario === 4) {
      setData(generateSyntheticPoints(walkActive));
    }
  }, [walkActive, scenario]);

  // Map raw data values to SVG coordinates & correlated vitals
  const points: Point[] = useMemo(() => {
    return data.map((val, i) => {
      const x = PAD_X + (i * (SIZE - 2 * PAD_X)) / (INITIAL_POINTS - 1);
      // Map 40-240 mg/dL to Y: 240 (bottom) to 60 (top)
      const y = 240 - ((val - 40) / 200) * 180;
      
      // Calculate correlated vitals
      const prevVal = i > 0 ? data[i - 1] ?? val : val;
      const delta = val - prevVal;
      const trend: 'rising' | 'falling' | 'stable' = 
        delta > 1.8 ? 'rising' : delta < -1.8 ? 'falling' : 'stable';
      
      // Heart rate correlates with activity & drops (tachycardia during lows)
      const hr = Math.round(val < 75 ? 98 + (75 - val) * 0.8 : 72 + Math.sin(i * 0.3) * 8);
      // Insulin on board decreases over the session
      const iob = Math.max(0, Number((2.8 - (i * 0.08)).toFixed(1)));

      return { x, y, val, idx: i, hr, iob, trend };
    });
  }, [data]);

  // Calculate spaces based on mapped points
  const spaces = useMemo(() => calculateSpaces(points), [points]);
  const largest = spaces[0];
  const secondLargest = spaces[1];

  // SVG Path generator
  const pathD = useMemo(() => {
    if (points.length === 0) return '';
    return `M ${points.map(p => `${p.x},${p.y}`).join(' L ')}`;
  }, [points]);

  // Scenario reset
  useEffect(() => {
    setSelectedPoints([]);
    setNotificationExpanded(false);
    if (scenario !== 5) {
      setIsStreaming(false);
    }
    if (scenario !== 4) {
      setWalkActive(false);
    }
  }, [scenario]);

  // Streaming Logic (Scenario 5)
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined;
    if (isStreaming) {
      interval = setInterval(() => {
        setData(prev => {
          tickRef.current += 1;
          const lastVal = prev[prev.length - 1] ?? 120;
          let newVal = lastVal + Math.sin(tickRef.current * 0.45) * 7 + (Math.random() * 8 - 4);
          newVal = Math.max(65, Math.min(225, newVal));
          return [...prev.slice(1), newVal];
        });
      }, 800);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isStreaming]);

  const handlePointClick = (idx: number) => {
    if (scenario === 1) {
      setSelectedPoints([idx]);
    } else if (scenario === 3) {
      setSelectedPoints(prev => {
        if (prev.length >= 2) return [idx];
        if (prev.includes(idx)) return prev.filter(i => i !== idx);
        return [...prev, idx];
      });
    }
  };

  const lastPoint = points[points.length - 1];
  const currentGlucose = lastPoint ? Math.round(lastPoint.val) : 120;
  const currentTrend = lastPoint?.trend ?? 'stable';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col items-center justify-center p-4 font-sans select-none">
      
      {/* HEADER & SCENARIOS BAR */}
      <div className="max-w-3xl w-full text-center mb-8">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Activity className="text-blue-500 w-6 h-6" />
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Glymmy Smartwatch UI
          </h1>
        </div>
        <p className="text-slate-400 mb-6 max-w-xl mx-auto text-xs sm:text-sm leading-relaxed">
          Circular SF-LG Space Allocation engine. Dynamically routes CGM, meal spike predictions, and wearable vitals into vacant screen pockets.
        </p>

        {/* Scenario Selectors */}
        <div className="flex flex-wrap justify-center gap-2">
          {[
            { id: 4, label: '🥗 S4: Meal Spike & Walk' },
            { id: 1, label: '📊 S1: Point Vitals' },
            { id: 2, label: '⚠️ S2: Rule of 15 Alert' },
            { id: 3, label: '⚖️ S3: Compare Points' },
            { id: 5, label: '⚡ S5: Live Stream' },
          ].map((s) => (
            <button
              key={s.id}
              onClick={() => setScenario(s.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                scenario === s.id 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30 ring-2 ring-blue-400/40' 
                  : 'bg-slate-800/90 text-slate-300 hover:bg-slate-700/80 border border-slate-700/50'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* SMARTWATCH HARDWARE MOCKUP */}
      <div className="relative flex items-center justify-center">
        
        {/* Watch Crown Button */}
        <div className="absolute -right-3 top-20 w-4 h-14 bg-gradient-to-b from-zinc-600 via-zinc-400 to-zinc-600 rounded-r-md border border-zinc-900 shadow-xl z-0"></div>

        {/* Circular Outer Bezel */}
        <div className="w-[336px] h-[336px] rounded-full bg-zinc-900 border-[3px] border-zinc-700 shadow-[0_25px_60px_rgba(0,0,0,0.9),inset_0_0_0_12px_#050505] p-[16px] relative z-10">
          
          {/* Watch Screen Display */}
          <div className="w-[300px] h-[300px] rounded-full bg-[#07090e] overflow-hidden relative border border-zinc-800/80 shadow-inner">
            
            {/* Top Status Bar: Time & Glance Complications */}
            <div className="absolute top-2 inset-x-0 flex flex-col items-center justify-center z-30 pointer-events-none">
              <span className="text-zinc-400 font-bold tracking-widest text-[10px] leading-tight mb-1">
                10:09
              </span>
              <div className="flex items-center justify-center gap-2">
                <span className="text-emerald-400 font-bold bg-emerald-950/80 border border-emerald-800/60 px-2 py-0.5 rounded-full text-[8.5px] leading-none shadow-sm">
                  TIR 84%
                </span>
                <span className="text-blue-400 font-bold bg-blue-950/80 border border-blue-800/60 px-2 py-0.5 rounded-full text-[8.5px] leading-none shadow-sm">
                  IOB 1.4U
                </span>
              </div>
            </div>

            {/* SVG CANVAS FOR CGM GRAPH & ALLOCATED ZONES */}
            <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="absolute inset-0 w-full h-full z-10">
              
              {/* Target Range Band (70 - 180 mg/dL) */}
              <rect x="20" y="114" width="260" height="63" fill="rgba(34, 197, 94, 0.05)" />
              <line x1="20" y1="114" x2="280" y2="114" stroke="rgba(34, 197, 94, 0.2)" strokeDasharray="3 3" />
              <line x1="20" y1="177" x2="280" y2="177" stroke="rgba(34, 197, 94, 0.2)" strokeDasharray="3 3" />
              <text x="24" y="173" fill="rgba(34, 197, 94, 0.4)" fontSize="8" fontWeight="bold">70 TARGET</text>

              {/* Visualized Allocated Spaces (SF-LG algorithm debug borders) */}
              {largest && (
                <rect 
                  x={largest.x} y={largest.y} width={largest.w} height={largest.h} 
                  fill="rgba(59, 130, 246, 0.04)" 
                  stroke="rgba(59, 130, 246, 0.2)" 
                  strokeDasharray="2" 
                  rx="6" 
                />
              )}
              {secondLargest && (
                <rect 
                  x={secondLargest.x} y={secondLargest.y} width={secondLargest.w} height={secondLargest.h} 
                  fill="rgba(168, 85, 247, 0.04)" 
                  stroke="rgba(168, 85, 247, 0.2)" 
                  strokeDasharray="2" 
                  rx="6" 
                />
              )}

              {/* CGM Data Line */}
              <path 
                d={pathD} 
                fill="none" 
                stroke={walkActive ? "#38bdf8" : "#f8fafc"} 
                strokeWidth="2.5" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                className="transition-all duration-700 ease-in-out"
                filter="drop-shadow(0 2px 5px rgba(0,0,0,0.8))" 
              />

              {/* Meal Event Pin (Scenario 4) */}
              {scenario === 4 && points[10] && (
                <g className="animate-in fade-in duration-300">
                  <line 
                    x1={points[10].x} y1={points[10].y} 
                    x2={points[10].x} y2={points[10].y - 20} 
                    stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="2" 
                  />
                  <circle cx={points[10].x} cy={points[10].y} r="3" fill="#f59e0b" />
                </g>
              )}

              {/* Current Value Marker */}
              {lastPoint && (
                <g>
                  <circle cx={lastPoint.x} cy={lastPoint.y} r="7" fill={currentGlucose < 70 ? "#ef4444" : "#3b82f6"} opacity="0.3" className="animate-ping" />
                  <circle cx={lastPoint.x} cy={lastPoint.y} r="4" fill={currentGlucose < 70 ? "#ef4444" : "#3b82f6"} stroke="#fff" strokeWidth="1.5" />
                </g>
              )}

              {/* Interactive Hit-Areas (S1 & S3) */}
              {points.map((p, i) => (
                <g key={i}>
                  <circle
                    cx={p.x} cy={p.y} r={13} fill="transparent"
                    className="cursor-pointer"
                    onClick={() => handlePointClick(i)}
                  />
                  {selectedPoints.includes(i) && (
                    <circle cx={p.x} cy={p.y} r={4.5} fill="#3b82f6" stroke="#fff" strokeWidth="1.5" className="pointer-events-none" />
                  )}
                </g>
              ))}
            </svg>

            {/* HTML OVERLAYS POSITIONED INSIDE ALLOCATED POCKETS */}
            <div className="absolute inset-0 pointer-events-none z-30">
              
              {/* SCENARIO 4: Meal Spike & Walk Advisor (Signature Feature) */}
              {scenario === 4 && largest && (
                <div 
                  className="absolute bg-zinc-900/95 border border-amber-500/40 rounded-xl p-2 flex flex-col justify-between shadow-2xl backdrop-blur-sm pointer-events-auto transition-all duration-500"
                  style={{ left: largest.x, top: largest.y, width: largest.w, height: largest.h }}
                >
                  <div className="flex items-center justify-between gap-1 border-b border-zinc-800 pb-1">
                    <div className="flex items-center gap-1">
                      <Utensils size={10} className="text-amber-400" />
                      <span className="text-[9px] font-bold text-amber-400">Lunch: 52g Carbs</span>
                    </div>
                    <span className="text-[8px] text-zinc-400">12:30 PM</span>
                  </div>

                  <div className="flex items-center justify-between text-[10px] my-0.5">
                    <span className="text-zinc-400">Predicted Peak:</span>
                    <span className={`font-extrabold ${walkActive ? 'text-emerald-400' : 'text-amber-300'}`}>
                      {walkActive ? '138 mg/dL' : '192 mg/dL'}
                    </span>
                  </div>

                  {/* Interactive Walk Button inside the watch pocket */}
                  <button
                    onClick={() => setWalkActive(!walkActive)}
                    className={`w-full py-1 px-1.5 rounded-lg text-[9px] font-bold flex items-center justify-center gap-1 transition-all ${
                      walkActive 
                        ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30' 
                        : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700'
                    }`}
                  >
                    {walkActive ? (
                      <>
                        <Check size={10} className="text-white" />
                        <span>Walk Active (-25 mg/dL)</span>
                      </>
                    ) : (
                      <>
                        <Footprints size={10} className="text-blue-400" />
                        <span>Simulate 15-min Walk</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* SCENARIO 1: Details on Demand with Correlated Wearable Vitals */}
              {scenario === 1 && selectedPoints.length > 0 && selectedPoints[0] !== undefined && points[selectedPoints[0]] && largest && (
                <div 
                  className="absolute bg-zinc-900/95 border border-blue-500/50 rounded-xl p-2 flex flex-col justify-between animate-in fade-in zoom-in duration-200 pointer-events-auto shadow-2xl backdrop-blur-sm"
                  style={{ left: largest.x, top: largest.y, width: largest.w, height: largest.h }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-baseline gap-1">
                      <span className="text-white text-xl font-black leading-none">
                        {Math.round(points[selectedPoints[0]].val)}
                      </span>
                      <span className="text-[8px] text-zinc-400 uppercase font-semibold">mg/dL</span>
                    </div>
                    {points[selectedPoints[0]].trend === 'rising' && <ArrowUpRight size={13} className="text-amber-400" />}
                    {points[selectedPoints[0]].trend === 'falling' && <ArrowDownRight size={13} className="text-emerald-400" />}
                    {points[selectedPoints[0]].trend === 'stable' && <ArrowRight size={13} className="text-zinc-400" />}
                  </div>

                  <div className="grid grid-cols-2 gap-1 pt-1 border-t border-zinc-800 text-[9px]">
                    <div className="flex items-center gap-1 text-red-400 font-medium">
                      <Heart size={9} />
                      <span>{points[selectedPoints[0]].hr} bpm</span>
                    </div>
                    <div className="flex items-center gap-1 text-blue-400 font-medium justify-end">
                      <span>IOB {points[selectedPoints[0]].iob}U</span>
                    </div>
                  </div>
                </div>
              )}
              {scenario === 1 && selectedPoints.length === 0 && (
                <div className="absolute inset-x-0 top-[45%] flex justify-center">
                  <span className="bg-zinc-800/90 text-zinc-300 text-[10px] px-3 py-1 rounded-full border border-zinc-700 shadow-md">
                    Tap any point on the line
                  </span>
                </div>
              )}

              {/* SCENARIO 2: Multi-Level Details & Rule of 15 Rescue */}
              {scenario === 2 && (
                <>
                  {/* Alert Icon in the second largest space */}
                  {secondLargest && (
                    <div 
                      className={`absolute flex items-center justify-center transition-all duration-300 pointer-events-auto cursor-pointer
                        ${notificationExpanded ? 'opacity-40 scale-90' : 'opacity-100 scale-100 hover:scale-105'}`}
                      style={{ left: secondLargest.x, top: secondLargest.y, width: secondLargest.w, height: secondLargest.h }}
                      onClick={() => setNotificationExpanded(!notificationExpanded)}
                    >
                      <div className="bg-red-500/20 p-2 rounded-full border border-red-500/50 animate-pulse">
                        <AlertTriangle size={15} className="text-red-500" />
                      </div>
                    </div>
                  )}

                  {/* Expanded Alert Details in the largest space */}
                  {notificationExpanded && largest && (
                    <div 
                      className="absolute bg-zinc-900/95 border border-red-500/60 rounded-xl p-2 flex flex-col justify-between animate-in fade-in zoom-in duration-200 pointer-events-auto cursor-pointer shadow-2xl"
                      style={{ left: largest.x, top: largest.y, width: largest.w, height: largest.h }}
                      onClick={() => setNotificationExpanded(false)}
                    >
                      <div className="flex items-center gap-1">
                        <AlertTriangle size={11} className="text-red-400" />
                        <span className="text-red-400 text-[9px] font-bold uppercase tracking-wide">Rapid Drop (64 mg/dL)</span>
                      </div>
                      <p className="text-zinc-200 text-[9px] leading-tight font-medium my-0.5">
                        <span className="text-amber-300 font-bold">Rule of 15:</span> Eat 15g fast carbs (juice/tabs). Retest in 15m.
                      </p>
                      <div className="text-[8px] text-zinc-400 flex justify-between border-t border-zinc-800/80 pt-0.5">
                        <span>Tap to dismiss</span>
                        <span className="text-emerald-400 font-semibold">HR 102 bpm</span>
                      </div>
                    </div>
                  )}
                  
                  {!notificationExpanded && secondLargest && (
                    <div className="absolute inset-x-0 bottom-[14%] flex justify-center">
                      <span className="bg-zinc-800/90 text-zinc-300 text-[10px] px-3 py-1 rounded-full border border-zinc-700 shadow-md">
                        Tap alert icon for rescue steps
                      </span>
                    </div>
                  )}
                </>
              )}

              {/* SCENARIO 3: Comparative Analysis with Delta */}
              {scenario === 3 && selectedPoints.length > 0 && selectedPoints[0] !== undefined && points[selectedPoints[0]] && largest && (
                <ComparativeWidget 
                  space={largest} 
                  point={points[selectedPoints[0]]} 
                  label="Point A" 
                  color="blue" 
                />
              )}
              {scenario === 3 && selectedPoints.length > 1 && selectedPoints[1] !== undefined && points[selectedPoints[1]] && secondLargest && (
                <ComparativeWidget 
                  space={secondLargest} 
                  point={points[selectedPoints[1]]} 
                  label="Point B" 
                  color="purple" 
                  delta={points[selectedPoints[1]].val - (points[selectedPoints[0]]?.val ?? 0)}
                />
              )}
              {scenario === 3 && selectedPoints.length < 2 && (
                <div className="absolute inset-x-0 top-[45%] flex justify-center">
                  <span className="bg-zinc-800/90 text-zinc-300 text-[10px] px-3 py-1 rounded-full border border-zinc-700 shadow-md">
                    Tap 2 points to compare delta
                  </span>
                </div>
              )}

              {/* SCENARIO 5: Live Streaming & Space Repositioning */}
              {scenario === 5 && largest && (
                <div 
                  className="absolute bg-zinc-900/90 border border-blue-500/40 rounded-xl p-2 flex flex-col justify-between shadow-xl pointer-events-auto backdrop-blur-sm"
                  style={{ 
                    left: largest.x, top: largest.y, width: largest.w, height: largest.h,
                    transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)' 
                  }}
                >
                  <div className="flex items-center justify-between text-[9px] text-zinc-400">
                    <span>LIVE STREAM</span>
                    <span className="flex h-1.5 w-1.5 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                    </span>
                  </div>
                  <div className="text-white text-lg font-black leading-none my-0.5">
                    {currentGlucose} <span className="text-[8px] text-zinc-400 font-normal">mg/dL</span>
                  </div>
                  <div className="text-[8px] text-emerald-400 font-semibold truncate">
                    {currentTrend === 'rising' ? '↗ Rising steadily' : currentTrend === 'falling' ? '↘ Falling' : '→ Stable'}
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>

      {/* FOOTER CONTROLS & DESCRIPTIONS */}
      <div className="mt-7 max-w-md w-full flex flex-col items-center">
        {scenario === 4 && (
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center w-full text-xs text-slate-300 shadow-md">
            <div className="font-bold text-amber-400 mb-1 flex items-center justify-center gap-1.5">
              <Utensils size={13} /> Glymmy AI Post-Meal Spike Blunting
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              When a meal is logged, Glymmy predicts the glycemic curve. Clicking <strong className="text-white">&ldquo;Simulate 15-min Walk&rdquo;</strong> flattens the spike from 192 down to 138 mg/dL in real-time.
            </p>
          </div>
        )}

        {scenario === 2 && (
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center w-full text-xs text-slate-300 shadow-md">
            <div className="font-bold text-red-400 mb-1 flex items-center justify-center gap-1.5">
              <AlertTriangle size={13} /> Multi-Level Details: Rule of 15
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              A gentle ambient warning icon sits unobtrusively in a vacant valley. Tapping it opens actionable clinical guidance without occluding the chart.
            </p>
          </div>
        )}

        {scenario === 5 && (
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-xs font-bold shadow-lg transition-all active:scale-95"
          >
            {isStreaming ? <Pause size={14} /> : <Play size={14} />} 
            {isStreaming ? 'Pause Stream' : 'Start Live Stream'}
          </button>
        )}
      </div>

    </div>
  );
}

// --- SUBCOMPONENTS ---

interface ComparativeWidgetProps {
  space: Space;
  point: Point;
  label: string;
  color: 'blue' | 'purple';
  delta?: number;
}

const ComparativeWidget: FC<ComparativeWidgetProps> = ({ space, point, label, color, delta }) => {
  const isBlue = color === 'blue';
  return (
    <div 
      className={`absolute bg-zinc-900/95 border rounded-xl p-1.5 flex flex-col justify-between animate-in zoom-in duration-200 pointer-events-auto shadow-xl backdrop-blur-sm ${
        isBlue ? 'border-blue-500/40 text-blue-400' : 'border-purple-500/40 text-purple-400'
      }`}
      style={{ left: space.x, top: space.y, width: space.w, height: space.h }}
    >
      <div className="flex items-center justify-between text-[8px] uppercase tracking-wider font-bold">
        <span>{label}</span>
        {delta !== undefined && (
          <span className={`px-1 py-0.2 rounded font-black ${delta > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {delta > 0 ? `+${Math.round(delta)}` : Math.round(delta)}
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-1 my-0.5">
        <span className="text-white font-extrabold text-base leading-none">{Math.round(point.val)}</span>
        <span className="text-[8px] text-zinc-400">mg/dL</span>
      </div>
      <div className="text-[8px] text-zinc-400 flex items-center gap-1">
        <Heart size={8} className="text-red-400" />
        <span>{point.hr} bpm</span>
      </div>
    </div>
  );
};
