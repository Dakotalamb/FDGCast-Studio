#!/usr/bin/env python3
"""Apply a reproducible, source-level FDGCast Studio navigation/UI patch.

Intentionally preserves the OBS streaming engine and dock APIs.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
candidates = [p for p in root.glob("frontend/**/window-basic-main.cpp") if p.is_file()]
candidates += [p for p in root.glob("frontend/**/OBSBasic.cpp") if p.is_file()]
if not candidates:
    raise SystemExit("OBSBasic implementation not found in extracted source")
target = candidates[0]
source = target.read_text(encoding="utf-8-sig")
if "FDGCAST_NAVIGATION_V2" in source:
    print("FDGCast UI patch already applied")
    raise SystemExit(0)

constructor = re.search(r"OBSBasic::OBSBasic\s*\([^;{}]*\)\s*(?::[^{}]*?)?\s*\{", source, re.S)
if not constructor:
    raise SystemExit(f"OBSBasic constructor not found in {target}; no changes applied")

includes = """#include <QTimer>
#include <QMenuBar>
#include <QMenu>
#include <QDockWidget>
#include <QAction>
#include <QToolBar>
#include <QLabel>
#include <QStatusBar>
#include <QSizePolicy>
#include <QFrame>
#include <QStringList>
#include <QPoint>
"""
code = r"""
    // FDGCAST_NAVIGATION_V2 — source-level usability layer.
    // Wait until OBS and companion plugins have had an opportunity to create docks.
    QTimer::singleShot(1500, this, [this]() {
        auto *bar = menuBar();
        if (!bar)
            return;

        // Preserve OBS's existing menus and controls; make common operations easier to find.
        auto *streamMenu = bar->addMenu(tr("Go Live"));
        auto *chatMenu = bar->addMenu(tr("Chat"));
        auto *eventsMenu = bar->addMenu(tr("Events"));
        auto *healthMenu = bar->addMenu(tr("Stream Health"));
        auto *workspaceMenu = bar->addMenu(tr("Workspace"));
        auto *guideMenu = bar->addMenu(tr("Getting Started"));

        auto addDockActions = [this](QMenu *menu, const QStringList &keywords) {
            menu->clear();
            for (auto *dock : findChildren<QDockWidget *>()) {
                if (!dock)
                    continue;
                const QString title = dock->windowTitle();
                bool matches = keywords.isEmpty();
                for (const auto &keyword : keywords)
                    if (title.contains(keyword, Qt::CaseInsensitive))
                        matches = true;
                if (matches && dock->toggleViewAction())
                    menu->addAction(dock->toggleViewAction());
            }
            if (menu->actions().isEmpty()) {
                auto *empty = menu->addAction(tr("No matching panels installed"));
                empty->setEnabled(false);
            }
        };
        connect(streamMenu, &QMenu::aboutToShow, this, [=]() {
            addDockActions(streamMenu, {QStringLiteral("multistream"), QStringLiteral("vertical")});
        });
        connect(chatMenu, &QMenu::aboutToShow, this, [=]() {
            addDockActions(chatMenu, {QStringLiteral("chat")});
        });
        connect(eventsMenu, &QMenu::aboutToShow, this, [=]() {
            addDockActions(eventsMenu, {QStringLiteral("event"), QStringLiteral("activity")});
        });
        connect(healthMenu, &QMenu::aboutToShow, this, [=]() {
            addDockActions(healthMenu, {QStringLiteral("doctor"), QStringLiteral("audio guard")});
        });
        connect(workspaceMenu, &QMenu::aboutToShow, this, [=]() {
            addDockActions(workspaceMenu, {});
            workspaceMenu->addSeparator();
            auto *showAll = workspaceMenu->addAction(tr("Show all panels"));
            connect(showAll, &QAction::triggered, this, [this]() {
                for (auto *dock : findChildren<QDockWidget *>())
                    if (dock) dock->show();
            });
        });

        auto *gettingStarted = guideMenu->addAction(tr("How to start streaming"));
        connect(gettingStarted, &QAction::triggered, this, [this]() {
            auto *help = new QMessageBox(QMessageBox::Information,
                tr("Getting started with FDGCast Studio"),
                tr("1. Add a Scene and Sources.\n"
                   "2. Check Audio Mixer levels.\n"
                   "3. Open Go Live to check platform connections.\n"
                   "4. Check Stream Health for warnings.\n"
                   "5. Use Start Streaming when ready.\n\n"
                   "You can show or hide panels from Workspace."),
                QMessageBox::Ok, this);
            help->setAttribute(Qt::WA_DeleteOnClose);
            help->show();
        });

        // A lightweight navigation strip above the existing OBS workspace.
        auto *navigation = new QToolBar(tr("FDGCast Quick Access"), this);
        navigation->setObjectName(QStringLiteral("FDGCastQuickAccess"));
        navigation->setMovable(false);
        navigation->setFloatable(false);
        navigation->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
        addToolBar(Qt::TopToolBarArea, navigation);
        auto *heading = new QLabel(tr("  FDGCast Studio  |  "), navigation);
        heading->setStyleSheet(QStringLiteral("font-weight: 700; padding: 4px;"));
        navigation->addWidget(heading);
        auto addQuickMenu = [navigation](const QString &name, QMenu *menu) {
            auto *action = navigation->addAction(name);
            QObject::connect(action, &QAction::triggered, navigation, [navigation, action, menu]() {
                auto *widget = navigation->widgetForAction(action);
                if (widget)
                    menu->popup(widget->mapToGlobal(QPoint(0, widget->height())));
            });
        };
        addQuickMenu(tr("Go Live"), streamMenu);
        addQuickMenu(tr("Chat"), chatMenu);
        addQuickMenu(tr("Events"), eventsMenu);
        addQuickMenu(tr("Stream Health"), healthMenu);
        addQuickMenu(tr("Workspace"), workspaceMenu);
        addQuickMenu(tr("Help"), guideMenu);
        setWindowTitle(tr("FDGCast Studio — Alpha"));
        statusBar()->showMessage(tr("FDGCast Studio ready — use Go Live to manage platforms"), 8000);
    });
"""
s=includes+"#include <QMessageBox>
"+source;const m=re.search(/OBSBasic::OBSBasics*([^;{}]*)s*(?::[^{}]*?)?s*{/s,s);if(!m)throw Error("constructor not found in script");s=s.slice(0,m.index+m[0].length)+"
"+code+s.slice(m.index+m[0].length);target.write_text(s,encoding="utf-8")
print(f"Applied FDGCast Studio UI navigation patch to {target}")
