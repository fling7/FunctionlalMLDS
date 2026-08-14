import React, { forwardRef, useCallback, useState } from "react";

const UnityLoader = forwardRef(function UnityLoader(
  { expanded, onToggleExpanded },
  ref,
) {
  const [loaded, setLoaded] = useState(false);

  const handleLoad = useCallback(() => {
    setLoaded(true);
  }, []);

  return (
    <section
      className={`experience-panel${expanded ? " experience-panel--expanded" : ""}`}
      aria-label="Virtueller Messestand"
    >
      <div className="experience-toolbar">
        <div>
          <span className="eyebrow eyebrow--light">3D-Ansicht</span>
          <h2>Virtueller Messestand</h2>
        </div>
        <div className="experience-actions">
          <button
            className="toolbar-button"
            type="button"
            onClick={onToggleExpanded}
            aria-pressed={expanded}
          >
            {expanded ? "Verkleinern" : "Ansicht vergrößern"}
          </button>
        </div>
      </div>

      <div className="unity-frame-wrap">
        {!loaded && (
          <div className="unity-placeholder" aria-live="polite">
            <span className="loading-mark" aria-hidden="true" />
            <strong>3D-Ansicht wird vorbereitet</strong>
            <span>Der erste Start kann einen Moment dauern.</span>
          </div>
        )}
        <iframe
          ref={ref}
          className="unity-frame"
          src="/BuildOutput/index.html?backend=%2Fnpc-api"
          title="Interaktiver virtueller Messestand Käsesteinpilz"
          allow="autoplay; fullscreen; microphone; xr-spatial-tracking"
          allowFullScreen
          onLoad={handleLoad}
        />
      </div>

      <div className="control-strip" aria-label="Hinweise zur Bedienung">
        <span><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> bewegen</span>
        <span className="control-pointer">Maus ziehen, um sich umzusehen</span>
        <span className="control-pointer"><kbd>Esc</kbd> gibt den Mauszeiger frei</span>
        <span><kbd>T</kbd> Texteingabe</span>
        <span><kbd>V</kbd> drücken und halten zum Sprechen</span>
        <span><kbd>E</kbd> Objekte auswählen</span>
      </div>
    </section>
  );
});

export default UnityLoader;
