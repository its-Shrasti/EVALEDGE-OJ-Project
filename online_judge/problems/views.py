from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from pathlib import Path
from .models import Problem , TestCase, Submission
from .forms import ProblemForm, SubmissionForm
import os
import uuid
import subprocess
import sys

@login_required
def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'problem_list.html', {'problems': problems})


@login_required
def add_problem(request):
    if request.user.role != 'setter':
        return redirect('problem_list')

    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.created_by = request.user
            problem.save()

            # Split lines from input and output textareas
            inputs = form.cleaned_data.get('raw_inputs', '').strip().split('\n')
            outputs = form.cleaned_data.get('raw_outputs', '').strip().split('\n')

            # Zip and create TestCase objects
            for i, o in zip(inputs, outputs):
                if i.strip() and o.strip():
                    TestCase.objects.create(input=i.strip(), expected_output=o.strip(), problem=problem)

            return redirect('problem_list')
    else:
        form = ProblemForm()
    
    return render(request, 'add_problem.html', {'form': form})



import google.generativeai as genai
import markdown

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    ai_feedback = None
    submitted_language = 'py'
    submitted_code = ''

    if request.method == "POST":
        submitted_language = request.POST.get("language", "py")
        submitted_code = request.POST.get("code", "")
        #print("POST data:", request.POST.dict())

        action = request.POST.get("action")
        #print("Action received:", action)
        if action == "ai_review":
            prompt = (
                "You are a code reviewer for a competitive programming judge. "
                "Given a problem and a user-submitted solution, review the code for correctness, "
                "efficiency, and coding style. Provide suggestions for improvement if needed.\n\n"
                f"Problem Description:\n{problem.description}\n\n"
                f"Language: {submitted_language}\n"
                f"User Code:\n{submitted_code}"
            )

            api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
            if not api_key:
                ai_feedback = "<p style='color:red;'>⚠️ GEMINI_API_KEY is not set.</p>"
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(prompt)
                    raw_md = response.text
                    ai_feedback = markdown.markdown(
                        raw_md,
                        extensions=["fenced_code", "codehilite", "nl2br"]
                    )
                except Exception as e:
                    ai_feedback = f"<pre style='color:red'>AI review unavailable: {e}</pre>"

        elif action == "run":
            # Handle run logic here
            pass
        elif action == "submit":
            # Handle submit logic here
            pass

    context = {
        "problem": problem,
        "ai_feedback": ai_feedback,
        "submitted_language": submitted_language,
        "submitted_code": submitted_code,
    }
    return render(request, 'problem_detail.html', context)



@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        lang = request.POST.get('language')
        action = request.POST.get('action')
        custom_input = request.POST.get('custom_input', '')

        if lang not in ['c', 'cpp', 'py']:
            return render(request, 'problem_detail.html', {
                'problem': problem,
                'error': 'Unsupported programming language selected.',
                'submitted_code': code,
                'submitted_language': lang,
                'custom_input': custom_input,
            })

        if action == 'run':
            # Run code on custom input only
            run_output = run_code(lang, code, custom_input)
            return render(request, 'problem_detail.html', {
                'problem': problem,
                'run_output': run_output,
                'submitted_code': code,
                'submitted_language': lang,
                'custom_input': custom_input,
            })

        elif action == 'submit':
            # Run code on all testcases
            testcases = TestCase.objects.filter(problem=problem)
            verdict = "Accepted"
            failed_case = None
            run_output = None
            error_message = None

            for idx, testcase in enumerate(testcases, 1):
                output = run_code(lang, code, testcase.input)

                if output.startswith("Compilation Error:") or output.startswith("Runtime Error:"):
                    verdict = output.split(":", 1)[0]
                    error_message = output
                    failed_case = idx
                    run_output = output
                    break

                if output.strip() != testcase.expected_output.strip():
                    verdict = "Wrong Answer"
                    failed_case = idx
                    run_output = output
                    break

            # Save submission
            Submission.objects.create(
                problem=problem,
                user=request.user,
                code=code,
                language=lang,
                verdict=verdict,
                submitted_at=timezone.now()
            )

            return render(request, 'problem_detail.html', {
                'problem': problem,
                'verdict': verdict,
                'failed_case': failed_case,
                'error_message': error_message,
                'run_output': run_output,
                'submitted_code': code,
                'submitted_language': lang,
                'custom_input': custom_input,
            })

    else:
        return redirect('problem_detail', problem_id=problem.id)

        




def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    for directory in [codes_dir, inputs_dir, outputs_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    unique = str(uuid.uuid4())
    code_file = codes_dir / f"{unique}.{language}"
    input_file = inputs_dir / f"{unique}.txt"
    output_file = outputs_dir / f"{unique}.txt"
    exe_path = codes_dir / unique  # for compiled executables

    with open(code_file, "w") as f:
        f.write(code)
    with open(input_file, "w") as f:
        f.write(input_data)

    try:
        if language in ["c", "cpp"]:
            compiler = "gcc" if language == "c" else "g++"
            compile_proc = subprocess.run(
                [compiler, str(code_file), "-o", str(exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            if compile_proc.returncode != 0:
                return f"Compilation Error:\n{compile_proc.stderr}"

            with open(input_file, "r") as infile, open(output_file, "w") as outfile:
                exec_proc = subprocess.run(
                    [str(exe_path)],
                    stdin=infile,
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
            if exec_proc.returncode != 0:
                return f"Runtime Error:\n{exec_proc.stderr}"

        elif language == "py":
            with open(input_file, "r") as infile, open(output_file, "w") as outfile:
                exec_proc = subprocess.run(
                    [sys.executable, str(code_file)],
                    stdin=infile,
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
            if exec_proc.returncode != 0:
                return f"Runtime Error:\n{exec_proc.stderr}"

        else:
            return "Unsupported language"

        with open(output_file, "r") as f:
            output = f.read()

        return output

    finally:
        # Cleanup all temp files
        for path in [code_file, input_file, output_file, exe_path]:
            if path and path.exists():
                path.unlink()




'''from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from google import genai # Note: the correct import is `google.generativeai`

@require_POST
@csrf_exempt  # Remove this if you handle CSRF in your AJAX
def ai_review_code(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)

        # Initialize Gemini client
        genai.configure(api_key="YOUR_API_KEY")  # Use your actual API key here

        # Generate content
        model = genai.GenerativeModel('gemini-2.0-flash')  # or 'gemini-2.0-pro', etc.
        prompt = f"Review this code for correctness, clarity, and style. Provide suggestions for improvement:\n\n{code}"
        response = model.generate_content(prompt)
        review = response.text

        return JsonResponse({'review': review})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)'''


