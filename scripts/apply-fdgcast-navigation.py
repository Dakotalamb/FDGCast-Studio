#!/usr/bin/env python3
"""Inject an initial FDGCast navigation layer into the OBS frontend source archive.
Fails closed if the expected upstream constructor is not found.
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
candidates = list(root.glob("frontend/**/OBSBasic.cpp")) + list(root.glob("frontend/**/window-basic-main.cpp"))
candidates = [p for p in candidates if p.is_file()]
if not candidates:
    raise SystemExit("No OBSBasic frontend implementation found; cannot apply navigation patch")
target = next((p for p in candidates if "window-basic-main" in p.name), candidates[0])
source = target.read_text(encoding="utf-8-sig")
if "FDGCAST_NAVIGATION_V1" in source:
    print("FDGCast navigation already present")
    raise SystemExit(0)

match = re.search(r"OBSBasic::OBSBasic\s*\([^;{}]*\)\s*(?::[^{}]*?)?\s*\{", source, re.S)
if not match:
    raise SystemExit(f"Could not locate OBSBasic constructor in {target}; leaving source unchanged")

# Qt menu controls are inserted after the constructor has completed initialization.
includes = """
#include <QTimer>
#include <QMenuBar>
#include <QMenu>
#include <QDockWidget>
#include <QAction>
#include <QPointer>
#include <QApplication>
"""
source = includes + source
match = re.search(r"OBSBasic::OBSBasic\s*\([^;{}]*\)\s*(?::[^{}]*?)?\s*\{", source, re.S)
code = r"""
    // FDGCAST_NAVIGATION_V1: initial source-level navigation, not a cosmetic installer change.
    QTimer::singleShot(0, this, [this]() {
        auto *bar = menuBar();
        if (!bar)
            return;
        auto *streamMenu = bar->addMenu(tr("Stream"));
        auto *chatMenu = bar->addMenu(tr("Chat"));
        auto *eventsMenu = bar->addMenu(tr("Events"));
        auto *healthMenu = bar->addMenu(tr("Stream Health"));
        auto *workspaceMenu = bar->addMenu(tr("Workspace"));

        const auto docks = findChildren<QDockWidget *>();
        for (auto *dock : docks) {
            if (!dock)
                continue;
            const QString title = dock->windowTitle();
            const QString lower = title.toLower();
            QMenu *destination = workspaceMenu;
            if (lower.contains(QStringLiteral("multistream")) ||
                lower.contains(QStringLiteral("vertical")))
                destination = streamMenu;
            else if (lower.contains(QStringLiteral("chat")))
                destination = chatMenu;
            else if (lower.contains(QStringLiteral("event")) ||
                     lower.contains(QStringLiteral("activity")))
                destination = eventsMenu;
            else if (lower.contains(QStringLiteral("doctor")) ||
                     lower.contains(QStringLiteral("audio guard")))
                destination = healthMenu;

            auto *action = dock->toggleViewAction();
            if (action)
                destination->addAction(action);
        }
        auto *restore = workspaceMenu->addAction(tr("Show all panels"));
        QObject::connect(restore, &QAction::triggered, this, [this]() {
            for (auto *dock : findChildren<QDockWidget *>())
                if (dock) dock->show();
        });
        setWindowTitle(tr("FDGCast Studio — Alpha"));
    });
"""
source = source[:match.end()] + "\n" + code + source[match.end():]
target.write_text(source, encoding="utf-8")
print(f"Patched {target}")
