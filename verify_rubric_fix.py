import asyncio

async def verify_rubric_editor_fix():
    print("🚀 Verifying Rubric Editor Fix...")
    
    # We can't easily run JS here, but we can verify the file content is correct
    with open("app/templates/exam_form.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    keyword = "const editorDiv = btn.closest('.rubric-editor'); // Correctly find the editor div"
    
    if keyword in content:
        print("✅ Fix detected in exam_form.html")
        print("   The function `addRubricRow` now uses `.closest('.rubric-editor')`")
    else:
        print("❌ Fix NOT found! File might not have been updated.")

if __name__ == "__main__":
    asyncio.run(verify_rubric_editor_fix())
