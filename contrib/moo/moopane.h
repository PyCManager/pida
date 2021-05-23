/*
 *   moopane.h
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

#ifndef MOO_INTERNAL_PANE_H
#define MOO_INTERNAL_PANE_H

#include <gtk/gtk.h>

G_BEGIN_DECLS


#define MOO_TYPE_INTERNAL_PANE               (moo_pane_get_type ())
#define MOO_INTERNAL_PANE(object)            (G_TYPE_CHECK_INSTANCE_CAST ((object), MOO_TYPE_INTERNAL_PANE, MooInternalPane))
#define MOO_INTERNAL_PANE_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST ((klass), MOO_TYPE_INTERNAL_PANE, MooInternalPaneClass))
#define MOO_IS_PANE(object)         (G_TYPE_CHECK_INSTANCE_TYPE ((object), MOO_TYPE_INTERNAL_PANE))
#define MOO_IS_PANE_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE ((klass), MOO_TYPE_INTERNAL_PANE))
#define MOO_INTERNAL_PANE_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS ((obj), MOO_TYPE_INTERNAL_PANE, MooInternalPaneClass))

#define MOO_TYPE_INTERNAL_PANE_LABEL         (moo_pane_label_get_type ())
#define MOO_TYPE_INTERNAL_PANE_PARAMS        (moo_pane_params_get_type ())

typedef struct MooInternalPane          MooInternalPane;
typedef struct MooInternalPaneClass     MooInternalPaneClass;
typedef struct MooInternalPaneLabel     MooInternalPaneLabel;
typedef struct MooInternalPaneParams    MooInternalPaneParams;

struct MooInternalPaneLabel {
    char *icon_stock_id;
    GdkPixbuf *icon_pixbuf;
    char *label;
    char *window_title;
};

struct MooInternalPaneParams
{
    GdkRectangle window_position;
    guint detached : 1;
    guint maximized : 1;
    guint keep_on_top : 1;
};


GType           moo_pane_get_type           (void) G_GNUC_CONST;
GType           moo_pane_label_get_type     (void) G_GNUC_CONST;
GType           moo_pane_params_get_type    (void) G_GNUC_CONST;

const char     *moo_pane_get_id             (MooInternalPane        *pane);

void            moo_pane_set_label          (MooInternalPane        *pane,
                                             MooInternalPaneLabel   *label);
/* result must be freed with moo_pane_label_free() */
MooInternalPaneLabel   *moo_pane_get_label          (MooInternalPane        *pane);
void            moo_pane_set_frame_markup   (MooInternalPane        *pane,
                                             const char     *markup);
void            moo_pane_set_frame_text     (MooInternalPane        *pane,
                                             const char     *text);
void            moo_pane_set_params         (MooInternalPane        *pane,
                                             MooInternalPaneParams  *params);
/* result must be freed with moo_pane_params_free() */
MooInternalPaneParams  *moo_pane_get_params         (MooInternalPane        *pane);
void            moo_pane_set_detachable     (MooInternalPane        *pane,
                                             gboolean        detachable);
gboolean        moo_pane_get_detachable     (MooInternalPane        *pane);
void            moo_pane_set_removable      (MooInternalPane        *pane,
                                             gboolean        removable);
gboolean        moo_pane_get_removable      (MooInternalPane        *pane);

GtkWidget      *moo_pane_get_child          (MooInternalPane        *pane);
int             moo_pane_get_index          (MooInternalPane        *pane);

void            moo_pane_open               (MooInternalPane        *pane);
void            moo_pane_present            (MooInternalPane        *pane);
void            moo_pane_attach             (MooInternalPane        *pane);
void            moo_pane_detach             (MooInternalPane        *pane);

void            moo_pane_set_drag_dest      (MooInternalPane        *pane);
void            moo_pane_unset_drag_dest    (MooInternalPane        *pane);

MooInternalPaneParams  *moo_pane_params_new         (GdkRectangle   *window_position,
                                             gboolean        detached,
                                             gboolean        maximized,
                                             gboolean        keep_on_top);
MooInternalPaneParams  *moo_pane_params_copy        (MooInternalPaneParams  *params);
void            moo_pane_params_free        (MooInternalPaneParams  *params);

MooInternalPaneLabel   *moo_pane_label_new          (const char     *icon_stock_id,
                                             GdkPixbuf      *pixbuf,
                                             const char     *label,
                                             const char     *window_title);
MooInternalPaneLabel   *moo_pane_label_copy         (MooInternalPaneLabel   *label);
void            moo_pane_label_free         (MooInternalPaneLabel   *label);

MooInternalPane        *_moo_pane_new               (GtkWidget      *child,
                                             MooInternalPaneLabel   *label);
void            _moo_pane_set_id            (MooInternalPane        *pane,
                                             const char     *id);

gpointer        _moo_pane_get_parent        (MooInternalPane        *pane);
GtkWidget      *_moo_pane_get_frame         (MooInternalPane        *pane);
void            _moo_pane_update_focus_child (MooInternalPane       *pane);
GtkWidget      *_moo_pane_get_focus_child   (MooInternalPane        *pane);
GtkWidget      *_moo_pane_get_button        (MooInternalPane        *pane);
void            _moo_pane_get_handle        (MooInternalPane        *pane,
                                             GtkWidget     **big,
                                             GtkWidget     **small);
GtkWidget      *_moo_pane_get_window        (MooInternalPane        *pane);

void            _moo_pane_params_changed    (MooInternalPane        *pane);
void            _moo_pane_freeze_params     (MooInternalPane        *pane);
void            _moo_pane_thaw_params       (MooInternalPane        *pane);
void            _moo_pane_size_request      (MooInternalPane        *pane,
                                             GtkRequisition *req);
void            _moo_pane_get_size_request  (MooInternalPane        *pane,
                                             GtkRequisition *req);
void            _moo_pane_size_allocate     (MooInternalPane        *pane,
                                             GtkAllocation  *allocation);

gboolean        _moo_pane_get_detached      (MooInternalPane        *pane);
void            _moo_pane_attach            (MooInternalPane        *pane);
void            _moo_pane_detach            (MooInternalPane        *pane);
void            _moo_pane_set_parent        (MooInternalPane        *pane,
                                             gpointer        parent,
                                             GdkWindow      *window);
void            _moo_pane_unparent          (MooInternalPane        *pane);
void            _moo_pane_try_remove        (MooInternalPane        *pane);

typedef enum {
    MOO_SMALL_ICON_HIDE,
    MOO_SMALL_ICON_STICKY,
    MOO_SMALL_ICON_CLOSE,
    MOO_SMALL_ICON_DETACH,
    MOO_SMALL_ICON_ATTACH,
    MOO_SMALL_ICON_KEEP_ON_TOP
} MooSmallIcon;

GtkWidget      *_moo_create_small_icon      (MooSmallIcon    icon);
GtkWidget      *_moo_create_arrow_icon      (GtkArrowType    arrow_type);


G_END_DECLS

#endif /* MOO_INTERNAL_PANE_H */
