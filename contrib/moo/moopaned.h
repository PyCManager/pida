/*
 *   moopaned.h
 *
 *   Copyright (C) 2004-2008 by Yevgen Muntyan <muntyan@tamu.edu>
 *
 *   This file is part of medit.  medit is free software; you can
 *   redistribute it and/or modify it under the terms of the
 *   GNU Lesser General Public License as published by the
 *   Free Software Foundation; either version 2.1 of the License,
 *   or (at your option) any later version.
 *
 *   You should have received a copy of the GNU Lesser General Public
 *   License along with medit.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef MOO_INTERNAL_PANED_H
#define MOO_INTERNAL_PANED_H

#include "moopane.h"
#include <gtk/gtkbin.h>

G_BEGIN_DECLS


#define MOO_TYPE_INTERNAL_PANED              (moo_paned_get_type ())
#define MOO_INTERNAL_PANED(object)           (G_TYPE_CHECK_INSTANCE_CAST ((object), MOO_TYPE_INTERNAL_PANED, MooInternalPaned))
#define MOO_INTERNAL_PANED_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST ((klass), MOO_TYPE_INTERNAL_PANED, MooInternalPanedClass))
#define MOO_IS_PANED(object)        (G_TYPE_CHECK_INSTANCE_TYPE ((object), MOO_TYPE_INTERNAL_PANED))
#define MOO_IS_PANED_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE ((klass), MOO_TYPE_INTERNAL_PANED))
#define MOO_INTERNAL_PANED_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS ((obj), MOO_TYPE_INTERNAL_PANED, MooInternalPanedClass))

#define MOO_TYPE_INTERNAL_PANE_POSITION      (moo_pane_position_get_type ())

typedef struct _MooInternalPaned         MooInternalPaned;
typedef struct _MooInternalPanedPrivate  MooInternalPanedPrivate;
typedef struct _MooInternalPanedClass    MooInternalPanedClass;

typedef enum {
    MOO_INTERNAL_PANE_POS_LEFT = 0,
    MOO_INTERNAL_PANE_POS_RIGHT,
    MOO_INTERNAL_PANE_POS_TOP,
    MOO_INTERNAL_PANE_POS_BOTTOM
} MooInternalPanePosition;

struct _MooInternalPaned
{
    GtkBin           bin;
    GtkWidget       *button_box;
    MooInternalPanedPrivate *priv;
};

struct _MooInternalPanedClass
{
    GtkBinClass bin_class;

    void (*set_pane_size)       (MooInternalPaned       *paned,
                                 int             size);

    void (*handle_drag_start)   (MooInternalPaned       *paned,
                                 GtkWidget      *pane_widget);
    void (*handle_drag_motion)  (MooInternalPaned       *paned,
                                 GtkWidget      *pane_widget);
    void (*handle_drag_end)     (MooInternalPaned       *paned,
                                 GtkWidget      *pane_widget,
                                 gboolean        drop);

    void (*pane_params_changed) (MooInternalPaned       *paned,
                                 guint           index_);
};


GType           moo_paned_get_type          (void) G_GNUC_CONST;
GType           moo_pane_position_get_type  (void) G_GNUC_CONST;

GtkWidget      *moo_paned_new               (MooInternalPanePosition pane_position);

MooInternalPane        *moo_paned_insert_pane       (MooInternalPaned       *paned,
                                             GtkWidget      *pane_widget,
                                             MooInternalPaneLabel   *pane_label,
                                             int             position);
gboolean        moo_paned_remove_pane       (MooInternalPaned       *paned,
                                             GtkWidget      *pane_widget);

guint           moo_paned_n_panes           (MooInternalPaned       *paned);
GSList         *moo_paned_list_panes        (MooInternalPaned       *paned);
MooInternalPane        *moo_paned_get_nth_pane      (MooInternalPaned       *paned,
                                             guint           n);
int             moo_paned_get_pane_num      (MooInternalPaned       *paned,
                                             GtkWidget      *widget);
MooInternalPane        *moo_paned_get_pane          (MooInternalPaned       *paned,
                                             GtkWidget      *widget);

void            moo_paned_set_sticky_pane   (MooInternalPaned       *paned,
                                             gboolean        sticky);

void            moo_paned_set_pane_size     (MooInternalPaned       *paned,
                                             int             size);
int             moo_paned_get_pane_size     (MooInternalPaned       *paned);
int             moo_paned_get_button_box_size (MooInternalPaned     *paned);

MooInternalPane        *moo_paned_get_open_pane     (MooInternalPaned       *paned);
gboolean        moo_paned_is_open           (MooInternalPaned       *paned);

void            moo_paned_open_pane         (MooInternalPaned       *paned,
                                             MooInternalPane        *pane);
void            moo_paned_present_pane      (MooInternalPaned       *paned,
                                             MooInternalPane        *pane);
void            moo_paned_hide_pane         (MooInternalPaned       *paned);
void            moo_paned_attach_pane       (MooInternalPaned       *paned,
                                             MooInternalPane        *pane);
void            moo_paned_detach_pane       (MooInternalPaned       *paned,
                                             MooInternalPane        *pane);

MooInternalPanePosition _moo_paned_get_position     (MooInternalPaned       *paned);
void            _moo_paned_attach_pane      (MooInternalPaned       *paned,
                                             MooInternalPane        *pane);
void            _moo_paned_insert_pane      (MooInternalPaned       *paned,
                                             MooInternalPane        *pane,
                                             int             position);
void            _moo_paned_reorder_child    (MooInternalPaned       *paned,
                                             MooInternalPane        *pane,
                                             int             position);
void            _moo_paned_get_button_position (MooInternalPaned    *paned,
                                             int             index,
                                             GdkRectangle   *rect,
                                             GdkWindow      *reference);
int             _moo_paned_get_button       (MooInternalPaned       *paned,
                                             int             x,
                                             int             y,
                                             GdkWindow      *reference);
int             _moo_paned_get_open_pane_index (MooInternalPaned    *paned);


G_END_DECLS

#endif /* MOO_INTERNAL_PANED_H */
