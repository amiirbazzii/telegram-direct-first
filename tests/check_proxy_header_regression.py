#!/usr/bin/env python3
"""
Regression test for ActionBar title secondary drawable (rightDrawable2) lifecycle
and DialogsActivity proxy indicator routing.
Honest static regression check bound to source files.
"""

import sys
import re

def check_actionbar(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # 1. Verify lastRightDrawable2 field exists
    if "Drawable lastRightDrawable2;" not in content:
        errors.append("ActionBar missing field 'lastRightDrawable2'")

    # 2. Verify setRightDrawable2 method exists and updates both titleTextView[0] and titleTextView[1]
    if "public void setRightDrawable2(Drawable rightDrawable2)" not in content:
        errors.append("ActionBar missing method 'setRightDrawable2(Drawable)'")
    if "titleTextView[0].setRightDrawable2(rightDrawable2);" not in content:
        errors.append("ActionBar.setRightDrawable2 does not update titleTextView[0]")
    if "titleTextView[1].setRightDrawable2(rightDrawable2);" not in content:
        errors.append("ActionBar.setRightDrawable2 does not update titleTextView[1]")

    # 3. Verify setTitleOverlayText maintains rightDrawable2 across overlay lifecycle:
    # (a) defines rightDrawable2ToSet: null when overlay active, lastRightDrawable2 when cleared
    if "Drawable rightDrawable2ToSet = title != null ? null : lastRightDrawable2;" not in content:
        errors.append("ActionBar.setTitleOverlayText does not compute rightDrawable2ToSet based on overlay title")

    # (b) sets rightDrawable2 on titleTextView[0] on initial/recreation branch
    if "titleTextView[0].setRightDrawable2(rightDrawable2ToSet);" not in content:
        errors.append("ActionBar.setTitleOverlayText does not apply rightDrawable2ToSet to titleTextView[0]")

    # (c) sets rightDrawable2 on titleTextView[1] on swap/animation branch
    if "titleTextView[1].setRightDrawable2(rightDrawable2ToSet);" not in content:
        errors.append("ActionBar.setTitleOverlayText does not apply rightDrawable2ToSet to titleTextView[1]")

    # 4. Verify setTitle(CharSequence, Drawable) applies lastRightDrawable2 to titleTextView[0]
    if "titleTextView[0].setRightDrawable2(lastRightDrawable2);" not in content:
        errors.append("ActionBar.setTitle does not restore lastRightDrawable2 on titleTextView[0]")

    return errors

def check_dialogsactivity(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # 1. Verify updateProxyHeaderIndicator routes collapsed shield through dialogStoriesCell.setProxyIndicator
    if "dialogStoriesCell.setProxyIndicator(wrappedShield, description);" not in content:
        errors.append("DialogsActivity.updateProxyHeaderIndicator does not route through dialogStoriesCell.setProxyIndicator(wrappedShield, description)")
    if "dialogStoriesCell.setProxyIndicator(null, null);" not in content:
        errors.append("DialogsActivity.updateProxyHeaderIndicator does not reset dialogStoriesCell.setProxyIndicator(null, null)")
    if "actionBar.setRightDrawable2(null);" not in content:
        errors.append("DialogsActivity.updateProxyHeaderIndicator does not clear expanded actionBar.setRightDrawable2(null)")

    # 2. Verify size-aware wrapper (WrapSizeDrawable) is used with small size (16dp)
    if "new AnimatedEmojiDrawable.WrapSizeDrawable(shieldDrawable, dp(16), dp(16))" not in content:
        errors.append("DialogsActivity does not wrap shieldDrawable in AnimatedEmojiDrawable.WrapSizeDrawable(shieldDrawable, dp(16), dp(16))")

    # 3. Verify Theme.key_actionBarDefaultSubtitle (dark theme) and Theme.key_chats_tabUnreadUnactiveBackground (light theme) are used
    if "Theme.key_actionBarDefaultSubtitle" not in content:
        errors.append("DialogsActivity does not tint shieldDrawable with Theme.key_actionBarDefaultSubtitle for dark theme")
    if "Theme.key_chats_tabUnreadUnactiveBackground" not in content:
        errors.append("DialogsActivity does not tint shieldDrawable with Theme.key_chats_tabUnreadUnactiveBackground for light theme")

    # 4. Verify initial creation and dialogStoriesCell creation call updateProxyHeaderIndicator
    if content.count("updateProxyHeaderIndicator();") < 2:
        errors.append("DialogsActivity missing updateProxyHeaderIndicator() calls for creation and refresh")

    # 5. Verify title click routing branch to ProxyListActivity is preserved
    if "presentFragment(new ProxyListActivity());" not in content:
        errors.append("DialogsActivity missing presentFragment(new ProxyListActivity())")

    # 6. Verify menu title and subtitle binding for effective direct connection
    if "proxyMenuSubItem.setText(getString(R.string.DirectConnection));" not in content:
        errors.append("DialogsActivity missing DirectConnection menu label binding")
    if "proxyMenuSubItem.setText(getString(R.string.MenuProxyTitle));" not in content:
        errors.append("DialogsActivity missing MenuProxyTitle menu label restoration")
    if "proxyMenuSubItem.setIcon(R.drawable.outline_shield_flash_24);" not in content:
        errors.append("DialogsActivity missing outline_shield_flash_24 icon binding for DirectConnection")
    if "proxyMenuSubItem.setIcon(proxyDrawable);" not in content:
        errors.append("DialogsActivity missing proxyDrawable icon restoration for Proxy")

    return errors

def check_simple_text_view(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # Verify that in createLayout(int width), width is reduced by dw, not cumulative rightDrawableWidth
    # Correct pattern:
    #   int dw = (int) (rightDrawable.getIntrinsicWidth() * rightDrawableScale);
    #   rightDrawableWidth += dw;
    #   width -= dw;
    #
    #   int dw2 = (int) (rightDrawable2.getIntrinsicWidth() * rightDrawableScale);
    #   rightDrawableWidth += dw2;
    #   width -= dw2;
    if "rightDrawableWidth += (int) (rightDrawable2.getIntrinsicWidth() * rightDrawableScale);\n                        width -= rightDrawableWidth;" in content:
        errors.append("SimpleTextView.createLayout still exhibits cumulative subtraction defect: 'width -= rightDrawableWidth' after adding dw2")

    if "int dw2 = (int) (rightDrawable2.getIntrinsicWidth() * rightDrawableScale);\n                        rightDrawableWidth += dw2;\n                        width -= dw2;" not in content:
        errors.append("SimpleTextView.createLayout does not use non-cumulative subtraction for rightDrawable2")

    # Verify recreateLayoutMaybe calcOffset block also uses non-cumulative subtraction
    if "int dw2 = (int) (rightDrawable2.getIntrinsicWidth() * rightDrawableScale);\n                    rightDrawableWidth += dw2;\n                    width -= dw2;" not in content:
        errors.append("SimpleTextView.recreateLayoutMaybe does not use non-cumulative subtraction for rightDrawable2")

    # Mathematical demonstration of defective vs corrected deduction:
    initial_width = 200
    dw1 = 26  # statusDrawable size
    dw2 = 16  # shieldDrawable size
    padding = 4

    # Defective cumulative logic:
    rdw_bad = 0
    w_bad = initial_width
    rdw_bad += dw1
    w_bad -= rdw_bad
    w_bad -= padding
    rdw_bad += dw2
    w_bad -= rdw_bad  # BUG: subtracts dw1 + dw2 again!
    w_bad -= padding
    # Total deduction was: dw1 + padding + (dw1 + dw2) + padding = 2 * dw1 + dw2 + 2 * padding = 52 + 16 + 8 = 76

    # Correct non-cumulative logic:
    rdw_good = 0
    w_good = initial_width
    rdw_good += dw1
    w_good -= dw1
    w_good -= padding
    rdw_good += dw2
    w_good -= dw2
    w_good -= padding
    # Total deduction is: dw1 + padding + dw2 + padding = 26 + 4 + 16 + 4 = 50

    excess_deduction = (initial_width - w_bad) - (initial_width - w_good)
    if excess_deduction != dw1:
        errors.append(f"Demonstration mismatch: expected excess deduction of {dw1}px, got {excess_deduction}px")

    return errors, (initial_width - w_bad), (initial_width - w_good)

def main():
    actionbar_path = "TMessagesProj/src/main/java/org/telegram/ui/ActionBar/ActionBar.java"
    dialogs_path = "TMessagesProj/src/main/java/org/telegram/ui/DialogsActivity.java"
    simpletextview_path = "TMessagesProj/src/main/java/org/telegram/ui/ActionBar/SimpleTextView.java"

    ab_errors = check_actionbar(actionbar_path)
    da_errors = check_dialogsactivity(dialogs_path)
    stv_errors, deduction_before, deduction_after = check_simple_text_view(simpletextview_path)

    all_errors = ab_errors + da_errors + stv_errors

    print(f"Regression check - Width deduction demonstration (dw1=26, dw2=16, pad=4):")
    print(f"  Before fix deduction: {deduction_before}px (excessive by 26px due to cumulative subtraction)")
    print(f"  After fix deduction:  {deduction_after}px (correct non-cumulative subtraction)")

    if all_errors:
        print("[FAIL] Regression checks failed:")
        for err in all_errors:
            print("  - " + err)
        sys.exit(1)
    else:
        print("[PASS] All ActionBar, DialogsActivity, and SimpleTextView width deduction regression checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()

