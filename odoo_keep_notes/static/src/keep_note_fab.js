/** @odoo-module **/

import { Component, xml, useState, onWillStart, useRef, useExternalListener } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class KeepNoteFab extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            isOpen: false,
            pinnedNotes: [],
            pos: { x: window.innerWidth - 90, y: window.innerHeight - 100 }
        });

        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.rootRef = useRef("root");

        useExternalListener(window, "mousedown", this.onWindowClick, { capture: true });
        useExternalListener(window, "touchstart", this.onWindowClick, { capture: true });

        onWillStart(async () => {
            await this.loadPinnedNotes();
        });
    }

    onWindowClick(ev) {
        if (this.state.isOpen && this.rootRef.el && !this.rootRef.el.contains(ev.target)) {
            this.state.isOpen = false;
        }
    }

    async loadPinnedNotes() {
        this.state.pinnedNotes = await this.orm.searchRead(
            "keep.note",
            [["is_pinned", "=", true], ["active", "=", true], ["is_trashed", "=", false]],
            ["id", "name"]
        );
    }

    onMouseDown(ev) {
        this.dragOffset = {
            x: ev.clientX - this.state.pos.x,
            y: ev.clientY - this.state.pos.y
        };
        this.dragStartX = ev.clientX;
        this.dragStartY = ev.clientY;
        this.isDragging = false;

        const onMouseMove = (moveEv) => {
            if (Math.abs(moveEv.clientX - this.dragStartX) > 5 || Math.abs(moveEv.clientY - this.dragStartY) > 5) {
                this.isDragging = true;
            }
            this.state.pos.x = moveEv.clientX - this.dragOffset.x;
            this.state.pos.y = moveEv.clientY - this.dragOffset.y;
        };

        const onMouseUp = () => {
            document.removeEventListener("mousemove", onMouseMove);
            document.removeEventListener("mouseup", onMouseUp);
        };

        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
    }

    onTouchStart(ev) {
        const touch = ev.touches[0];
        this.dragOffset = {
            x: touch.clientX - this.state.pos.x,
            y: touch.clientY - this.state.pos.y
        };
        this.dragStartX = touch.clientX;
        this.dragStartY = touch.clientY;
        this.isDragging = false;

        const onTouchMove = (moveEv) => {
            const t = moveEv.touches[0];
            if (Math.abs(t.clientX - this.dragStartX) > 5 || Math.abs(t.clientY - this.dragStartY) > 5) {
                this.isDragging = true;
            }
            this.state.pos.x = t.clientX - this.dragOffset.x;
            this.state.pos.y = t.clientY - this.dragOffset.y;
        };

        const onTouchEnd = () => {
            document.removeEventListener("touchmove", onTouchMove);
            document.removeEventListener("touchend", onTouchEnd);
        };

        document.addEventListener("touchmove", onTouchMove, { passive: false });
        document.addEventListener("touchend", onTouchEnd);
    }

    async onClick(ev) {
        if (this.isDragging) {
            this.isDragging = false;
            return; // Prevent click if we were dragging
        }

        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            await this.loadPinnedNotes();
        }
    }

    async createNewNote() {
        this.state.isOpen = false;
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "keep.note",
            views: [[false, "form"]],
            target: "new",
            name: "Take a Note",
            context: {
                form_view_initial_mode: 'edit',
            }
        });
    }

    async openNote(noteId) {
        this.state.isOpen = false;
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "keep.note",
            views: [[false, "form"]],
            res_id: noteId,
            target: "new",
        });
    }

    get popupStyle() {
        const x = this.state.pos.x;
        const y = this.state.pos.y;
        const w = window.innerWidth;
        const h = window.innerHeight;

        let style = "position: absolute; z-index: 1060; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); width: 250px; overflow: hidden; padding: 0; ";

        // Vertical positioning
        if (y > h / 2) {
            style += "bottom: 70px; ";
        } else {
            style += "top: 70px; ";
        }

        // Horizontal positioning
        if (x > w / 2) {
            style += "right: 0; ";
        } else {
            style += "left: 0; ";
        }

        return style;
    }
}

KeepNoteFab.template = xml`
    <div t-ref="root" t-att-style="'position: fixed; z-index: 1050; top: ' + state.pos.y + 'px; left: ' + state.pos.x + 'px;'">
        <t t-if="state.isOpen">
            <div t-att-style="popupStyle">
                 <div class="list-group list-group-flush">
                    <button class="list-group-item list-group-item-action text-primary fw-bold" t-on-click="createNewNote">
                        <i class="fa fa-plus me-2"></i> New Note
                    </button>
                    
                    <t t-if="state.pinnedNotes.length > 0">
                        <div class="list-group-item bg-light text-muted fw-bold small">PINNED NOTES</div>
                        <button t-foreach="state.pinnedNotes" t-as="note" t-key="note.id" 
                                class="list-group-item list-group-item-action"
                                t-on-click="() => this.openNote(note.id)">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1 text-truncate"><t t-esc="note.name || 'Untitled Note'"/></h6>
                            </div>
                        </button>
                    </t>
                 </div>
            </div>
        </t>

        <div class="o_keep_note_fab" 
             t-on-mousedown.prevent="onMouseDown"
             t-on-touchstart.prevent="onTouchStart"
             t-on-click="onClick" 
             style="background-color: #fbbc04; color: #333; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); cursor: grab; font-size: 24px;" 
             title="Keep Notes">
            <i class="fa fa-pencil"></i>
        </div>
    </div>
`;

registry.category("main_components").add("KeepNoteFab", {
    Component: KeepNoteFab,
});
