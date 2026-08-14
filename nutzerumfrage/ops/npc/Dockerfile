FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 1002 app \
    && python -m pip install --no-cache-dir jsonschema==4.25.1

WORKDIR /app/FunctionalMLDS
COPY --chown=app:app tools ./tools
COPY --chown=app:app InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents ./InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents

WORKDIR /app/FunctionalMLDS/InteractivAgents/openai_unity_expert_npcs_pycharm/InteractiveAgents
USER app
EXPOSE 8787
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/health', timeout=3).read()" || exit 1
CMD ["python", "-u", "main.py"]
