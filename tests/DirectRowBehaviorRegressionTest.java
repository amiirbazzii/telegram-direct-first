package org.telegram.apptests;

import java.io.File;
import java.lang.reflect.Method;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;

public class DirectRowBehaviorRegressionTest {

    private static String extractMethodBody(String source, String signature) {
        int idx = source.indexOf(signature);
        if (idx == -1) {
            throw new IllegalArgumentException("Method not found: " + signature);
        }
        int openBrace = source.indexOf('{', idx);
        int balance = 1;
        int i = openBrace + 1;
        while (i < source.length() && balance > 0) {
            char c = source.charAt(i);
            if (c == '{') balance++;
            else if (c == '}') balance--;
            i++;
        }
        return source.substring(idx, i);
    }

    public static void main(String[] args) throws Exception {
        System.out.println("Executing dynamic method extraction from ProxyListActivity.java...");

        File sourceFile = new File("TMessagesProj/src/main/java/org/telegram/ui/ProxyListActivity.java");
        String sourceContent = new String(Files.readAllBytes(sourceFile.toPath()));

        String setDirectCode = extractMethodBody(sourceContent, "public void setDirect()");
        String setSelectionEnabledCode = extractMethodBody(sourceContent, "public void setSelectionEnabled(boolean enabled, boolean animated)");

        StringBuilder sb = new StringBuilder();
        sb.append("package org.telegram.apptests.generated;\n\n");
        sb.append("public class ExtractedCellRunner {\n");
        sb.append("    public static final int VISIBLE = 0;\n");
        sb.append("    public static final int GONE = 8;\n\n");
        sb.append("    public static class Widget {\n");
        sb.append("        public int visibility = VISIBLE;\n");
        sb.append("        public float alpha = 1f, scaleX = 1f, scaleY = 1f, transX = 0f;\n");
        sb.append("        public void setVisibility(int v) { this.visibility = v; }\n");
        sb.append("        public void setAlpha(float a) { this.alpha = a; }\n");
        sb.append("        public void setScaleX(float s) { this.scaleX = s; }\n");
        sb.append("        public void setScaleY(float s) { this.scaleY = s; }\n");
        sb.append("        public void setTranslationX(float t) { this.transX = t; }\n");
        sb.append("        public void setText(CharSequence s) {}\n");
        sb.append("    }\n\n");
        sb.append("    public static class AndroidUtilities {\n");
        sb.append("        public static float dp(float val) { return val * 2; }\n");
        sb.append("        public static float lerp(float a, float b, float f) { return a + f * (b - a); }\n");
        sb.append("    }\n\n");
        sb.append("    public static class LocaleController {\n");
        sb.append("        public static boolean isRTL = false;\n");
        sb.append("    }\n\n");
        sb.append("    public static class CubicBezierInterpolator {\n");
        sb.append("        public static final Object DEFAULT = new Object();\n");
        sb.append("    }\n\n");
        sb.append("    public static class Animator {}\n\n");
        sb.append("    public static class AnimatorListenerAdapter {\n");
        sb.append("        public void onAnimationStart(Animator animation) {}\n");
        sb.append("        public void onAnimationEnd(Animator animation) {}\n");
        sb.append("    }\n\n");
        sb.append("    public interface ValueAnimatorUpdateListener {\n");
        sb.append("        void onAnimationUpdate(ValueAnimator animation);\n");
        sb.append("    }\n\n");
        sb.append("    public static class ValueAnimator {\n");
        sb.append("        private float animatedValue = 0f;\n");
        sb.append("        public static ValueAnimator ofFloat(float... vals) { return new ValueAnimator(); }\n");
        sb.append("        public ValueAnimator setDuration(long d) { return this; }\n");
        sb.append("        public void setInterpolator(Object o) {}\n");
        sb.append("        public void addUpdateListener(ValueAnimatorUpdateListener l) {\n");
        sb.append("            if (l != null) l.onAnimationUpdate(this);\n");
        sb.append("        }\n");
        sb.append("        public void addListener(AnimatorListenerAdapter l) {\n");
        sb.append("            if (l != null) {\n");
        sb.append("                l.onAnimationStart(new Animator());\n");
        sb.append("                l.onAnimationEnd(new Animator());\n");
        sb.append("            }\n");
        sb.append("        }\n");
        sb.append("        public void start() {}\n");
        sb.append("        public Object getAnimatedValue() { return animatedValue; }\n");
        sb.append("    }\n\n");
        sb.append("    public static class R {\n");
        sb.append("        public static class string {\n");
        sb.append("            public static final int DirectConnection = 1;\n");
        sb.append("        }\n");
        sb.append("    }\n\n");
        sb.append("    public Widget checkImageView = new Widget();\n");
        sb.append("    public Widget textView = new Widget();\n");
        sb.append("    public Widget valueTextView = new Widget();\n");
        sb.append("    public Widget checkBox = new Widget();\n");
        sb.append("    public boolean isSelectionEnabled = false;\n");
        sb.append("    public Object currentInfo = new Object();\n\n");
        sb.append("    public void updateStatus() {}\n");
        sb.append("    public String getString(int resId) { return \"Direct Connection\"; }\n\n");
        sb.append("    // Exact extracted setDirect method:\n");
        sb.append("    ").append(setDirectCode).append("\n\n");
        sb.append("    // Exact extracted setSelectionEnabled method (intact with full stubs):\n");
        sb.append("    ").append(setSelectionEnabledCode).append("\n");
        sb.append("}\n");

        File scratchDir = new File(System.getProperty("java.io.tmpdir"), "tg-craft-tests");
        scratchDir.mkdirs();

        File genJava = new File(scratchDir, "ExtractedCellRunner.java");
        Files.write(genJava.toPath(), sb.toString().getBytes());

        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        if (compiler == null) {
            throw new IllegalStateException("System JavaCompiler not found.");
        }

        int res = compiler.run(null, null, System.err, "-d", scratchDir.getAbsolutePath(), genJava.getAbsolutePath());
        if (res != 0) {
            throw new IllegalStateException("Compilation failed with exit code " + res);
        }

        URLClassLoader cl = new URLClassLoader(new URL[]{scratchDir.toURI().toURL()}, DirectRowBehaviorRegressionTest.class.getClassLoader());
        Class<?> runnerClass = cl.loadClass("org.telegram.apptests.generated.ExtractedCellRunner");
        Object cell = runnerClass.getDeclaredConstructor().newInstance();

        // 1. Call exact production setDirect()
        Method setDirectMethod = runnerClass.getMethod("setDirect");
        setDirectMethod.invoke(cell);

        Object checkImageView = runnerClass.getField("checkImageView").get(cell);
        int visAfterSetDirect = (int) checkImageView.getClass().getField("visibility").get(checkImageView);
        if (visAfterSetDirect != 8) {
            throw new AssertionError("setDirect() did not hide checkImageView (vis=" + visAfterSetDirect + ")");
        }

        // 2. Call exact production setSelectionEnabled(false, false)
        Method setSelectionEnabledMethod = runnerClass.getMethod("setSelectionEnabled", boolean.class, boolean.class);
        setSelectionEnabledMethod.invoke(cell, false, false);

        int visAfterNonAnimated = (int) checkImageView.getClass().getField("visibility").get(checkImageView);
        if (visAfterNonAnimated != 8) {
            System.err.println("[FAIL] Non-animated setSelectionEnabled made checkImageView visible! Expected GONE (8), got " + visAfterNonAnimated);
            System.exit(1);
        }

        // 3. Call exact production setSelectionEnabled(false, true) [animated path]
        setSelectionEnabledMethod.invoke(cell, false, true);
        int visAfterAnimated = (int) checkImageView.getClass().getField("visibility").get(checkImageView);
        if (visAfterAnimated != 8) {
            System.err.println("[FAIL] Animated setSelectionEnabled made checkImageView visible! Expected GONE (8), got " + visAfterAnimated);
            System.exit(1);
        }

        // 4. Static source checks
        System.out.println("[STATIC CHECK] Verifying static source contract in ProxyListActivity.java...");
        boolean directConditional = sourceContent.contains("directRow = proxyDirectFirst ? rowCount++ : -1;");
        boolean headerUnconditional = sourceContent.contains("connectionsHeaderRow = rowCount++;");
        boolean directFirstShadowAllocated = sourceContent.contains("directFirstShadowRow = rowCount++;");
        boolean directFirstShadowViewType = sourceContent.contains("position == directFirstShadowRow");
        boolean textCheckCellUsesValue = sourceContent.contains("checkCell.setTextAndValueAndCheck(getString(R.string.ProxyDirectFirst), getString(R.string.ProxyDirectFirstInfo), proxyDirectFirst, true, false);");

        String isEnabledMethod = extractMethodBody(sourceContent, "public boolean isEnabled(RecyclerView.ViewHolder holder)");
        boolean directDisabledInAdapter = !isEnabledMethod.contains("directRow");

        String onItemClick = extractMethodBody(sourceContent, "listView.setOnItemClickListener((view, position) ->");
        boolean directNotClickable = !onItemClick.contains("position == directRow");

        if (!directConditional || !headerUnconditional) {
            System.err.println("[STATIC FAILURE] directRow must be conditional on proxyDirectFirst and connectionsHeaderRow must be unconditional.");
            System.exit(1);
        }

        if (!directFirstShadowAllocated || !directFirstShadowViewType || !textCheckCellUsesValue) {
            System.err.println("[STATIC FAILURE] Direct first row must have directFirstShadowRow allocated as VIEW_TYPE_SHADOW to provide native card separation");
            System.exit(1);
        }

        if (!directDisabledInAdapter || !directNotClickable) {
            System.err.println("[STATIC FAILURE] directRow must be non-clickable (disabled in adapter and ignored in onItemClick)");
            System.exit(1);
        }

        System.out.println("[PASS] GREEN: All extracted cell and static row contracts passed.");
        System.exit(0);
    }
}
