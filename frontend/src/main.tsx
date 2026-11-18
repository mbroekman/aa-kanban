import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./index.css";

function isAllianceAuthDark(): boolean {
  const htmlTheme = document.documentElement.getAttribute("data-bs-theme");
  if (htmlTheme === "dark") return true;
  if (htmlTheme === "light") return false;

  const bodyTheme = document.body.getAttribute("data-bs-theme");
  if (bodyTheme === "dark") return true;
  if (bodyTheme === "light") return false;

  const bg = window.getComputedStyle(document.body).backgroundColor;
  const match = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    const r = Number(match[1]);
    const g = Number(match[2]);
    const b = Number(match[3]);
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    return luminance < 128;
  }
  return true;
}

function syncTheme(mountEl: HTMLElement) {
  mountEl.classList.toggle("dark", isAllianceAuthDark());
}

const mountEl = document.getElementById("aa-kanban-spa");
if (mountEl) {
  syncTheme(mountEl);

  const observer = new MutationObserver(() => syncTheme(mountEl));
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-bs-theme", "class"],
  });
  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["data-bs-theme", "class"],
  });

  createRoot(mountEl).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
}
