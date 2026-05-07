import type { PandaState } from "./state.js";

const SVG_NS = "http://www.w3.org/2000/svg";

function el<K extends keyof SVGElementTagNameMap>(
  tag: K,
  attrs: Record<string, string>,
): SVGElementTagNameMap[K] {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
}

export interface PandaFace {
  readonly svg: SVGSVGElement;
  setState(state: PandaState): void;
}

export function createPandaFace(): PandaFace {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 200 220");
  svg.setAttribute("xmlns", SVG_NS);
  svg.classList.add("panda-face");

  // ── Ears ──
  const earLeft = el("ellipse", { cx: "42", cy: "50", rx: "30", ry: "30", fill: "#1a1a1a", class: "panda-ear panda-ear-left" });
  const earRight = el("ellipse", { cx: "158", cy: "50", rx: "30", ry: "30", fill: "#1a1a1a", class: "panda-ear panda-ear-right" });

  // ── Face ──
  const face = el("ellipse", { cx: "100", cy: "115", rx: "85", ry: "90", fill: "#f5f5f0", class: "panda-face-body" });

  // ── Eye patches ──
  const patchLeft = el("ellipse", { cx: "68", cy: "100", rx: "26", ry: "22", fill: "#1a1a1a", transform: "rotate(-10 68 100)", class: "panda-patch" });
  const patchRight = el("ellipse", { cx: "132", cy: "100", rx: "26", ry: "22", fill: "#1a1a1a", transform: "rotate(10 132 100)", class: "panda-patch" });

  // ── Eyes (whites) ──
  const eyeWhiteLeft = el("ellipse", { cx: "68", cy: "100", rx: "13", ry: "13", fill: "#ffffff" });
  const eyeWhiteRight = el("ellipse", { cx: "132", cy: "100", rx: "13", ry: "13", fill: "#ffffff" });

  // ── Pupils ──
  const pupilLeft = el("ellipse", { cx: "70", cy: "101", rx: "7", ry: "8", fill: "#0a0a0a", class: "panda-pupil-left" });
  const pupilRight = el("ellipse", { cx: "130", cy: "101", rx: "7", ry: "8", fill: "#0a0a0a", class: "panda-pupil-right" });

  // ── Pupil shines ──
  const shineLeft = el("circle", { cx: "72", cy: "98", r: "2.5", fill: "#ffffff" });
  const shineRight = el("circle", { cx: "134", cy: "98", r: "2.5", fill: "#ffffff" });

  // ── Nose ──
  const nose = el("ellipse", { cx: "100", cy: "135", rx: "9", ry: "6", fill: "#1a1a1a" });

  // ── Mouth (closed default) ──
  const mouthGroup = el("g", { class: "panda-mouth" });
  const mouthClosed = el("path", { d: "M85 148 Q100 158 115 148", stroke: "#555", "stroke-width": "2.5", fill: "none", "stroke-linecap": "round", class: "mouth-closed" });
  const mouthOpen = el("path", { d: "M85 148 Q100 168 115 148 Q100 162 85 148", fill: "#c0392b", class: "mouth-open" });
  const mouthTongue = el("ellipse", { cx: "100", cy: "162", rx: "8", ry: "5", fill: "#e74c3c", class: "mouth-tongue" });

  // ── Cheek blushes ──
  const blushLeft = el("ellipse", { cx: "52", cy: "128", rx: "16", ry: "9", fill: "rgba(255,182,193,0.5)", class: "panda-blush" });
  const blushRight = el("ellipse", { cx: "148", cy: "128", rx: "16", ry: "9", fill: "rgba(255,182,193,0.5)", class: "panda-blush" });

  // ── Thinking dots (hidden by default) ──
  const thinkGroup = el("g", { class: "panda-think-dots" });
  const dot1 = el("circle", { cx: "130", cy: "60", r: "5", fill: "#888" });
  const dot2 = el("circle", { cx: "148", cy: "48", r: "7", fill: "#888" });
  const dot3 = el("circle", { cx: "168", cy: "34", r: "9", fill: "#888" });
  thinkGroup.append(dot1, dot2, dot3);

  mouthGroup.append(mouthClosed, mouthOpen, mouthTongue);

  svg.append(
    earLeft, earRight,
    face,
    patchLeft, patchRight,
    eyeWhiteLeft, eyeWhiteRight,
    pupilLeft, pupilRight,
    shineLeft, shineRight,
    blushLeft, blushRight,
    nose,
    mouthGroup,
    thinkGroup,
  );

  let mouthTimer: ReturnType<typeof setInterval> | null = null;

  function clearMouthTimer() {
    if (mouthTimer !== null) {
      clearInterval(mouthTimer);
      mouthTimer = null;
    }
  }

  function setState(state: PandaState) {
    clearMouthTimer();
    svg.dataset["state"] = state;

    if (state === "speaking") {
      let open = false;
      mouthTimer = setInterval(() => {
        open = !open;
        mouthGroup.dataset["open"] = open ? "1" : "0";
      }, 180);
    } else {
      mouthGroup.dataset["open"] = "0";
    }
  }

  setState("idle");

  return { svg, setState };
}
