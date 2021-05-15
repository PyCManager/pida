/*
 *   moobigpaned.h
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

#ifndef MOO_INTERNAL_BIG_PANED_H
#define MOO_INTERNAL_BIG_PANED_H

#include <gtk/gtkframe.h>
#include "moopaned.h"

G_BEGIN_DECLS


#define MOO_TYPE_INTERNAL_BIG_PANED              (moo_big_paned_get_type ())
#define MOO_INTERNAL_BIG_PANED(object)           (G_TYPE_CHECK_INSTANCE_CAST ((object), MOO_TYPE_INTERNAL_BIG_PANED, MooInternalBigPaned))
#define MOO_INTERNAL_BIG_PANED_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST ((klass), MOO_TYPE_INTERNAL_BIG_PANED, MooInternalBigPanedClass))
#define MOO_IS_BIG_PANED(object)        (G_TYPE_CHECK_INSTANCE_TYPE ((object), MOO_TYPE_INTERNAL_BIG_PANED))
#define MOO_IS_BIG_PANED_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE ((klass), MOO_TYPE_INTERNAL_BIG_PANED))
#define MOO_INTERNAL_BIG_PANED_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS ((obj), MOO_TYPE_INTERNAL_BIG_PANED, MooInternalBigPanedClass))


typedef struct MooInternalBigPaned        MooInternalBigPaned;
typedef struct MooInternalBigPanedPrivate MooInternalBigPanedPrivate;
typedef struct MooInternalBigPanedClass   MooInternalBigPanedClass;

struct MooInternalBigPaned
{
    GtkFrame base;
    MooInternalBigPanedPrivate *priv;
    GtkWidget *paned[4]; /* indexed by PanePos */
};

struct MooInternalBigPanedClass
{
    GtkFrameClass base_class;
};


GType           moo_big_paned_get_type          (void) G_GNUC_CONST;

GtkWidget      *moo_big_paned_new               (void);

void            moo_big_paned_set_pane_order    (MooInternalBigPaned    *paned,
                                                 int            *order);
void            moo_big_paned_set_config        (MooInternalBigPaned    *paned,
                                                 const char     *config_string);
char           *moo_big_paned_get_config        (MooInternalBigPaned    *paned);

MooInternalPane        *moo_big_paned_find_pane         (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget,
                                                 MooInternalPaned      **child_paned);

void            moo_big_paned_add_child         (MooInternalBigPaned    *paned,
                                                 GtkWidget      *widget);
void            moo_big_paned_remove_child      (MooInternalBigPaned    *paned);
GtkWidget      *moo_big_paned_get_child         (MooInternalBigPaned    *paned);

MooInternalPane        *moo_big_paned_insert_pane       (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget,
                                                 const char     *pane_id,
                                                 MooInternalPaneLabel   *pane_label,
                                                 MooInternalPanePosition position,
                                                 int             index_);
gboolean        moo_big_paned_remove_pane       (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget);
MooInternalPane        *moo_big_paned_lookup_pane       (MooInternalBigPaned    *paned,
                                                 const char     *pane_id);

GtkWidget      *moo_big_paned_get_pane          (MooInternalBigPaned    *paned,
                                                 MooInternalPanePosition position,
                                                 int             index_);
void            moo_big_paned_reorder_pane      (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget,
                                                 MooInternalPanePosition new_position,
                                                 int             new_index);

MooInternalPaned       *moo_big_paned_get_paned         (MooInternalBigPaned    *paned,
                                                 MooInternalPanePosition position);

void            moo_big_paned_open_pane         (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget);
void            moo_big_paned_hide_pane         (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget);
void            moo_big_paned_present_pane      (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget);
void            moo_big_paned_attach_pane       (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget);
void            moo_big_paned_detach_pane       (MooInternalBigPaned    *paned,
                                                 GtkWidget      *pane_widget);


G_END_DECLS

#endif /* MOO_INTERNAL_BIG_PANED_H */
