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



@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    return render(request, 'problem_detail.html', {'problem': problem})

        
@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        lang = request.POST.get('language')

        if lang not in ['c', 'cpp', 'py']:
            return render(request, 'problem_detail.html', {
                'problem': problem,
                'error': 'Unsupported programming language selected.'
            })

        testcases = TestCase.objects.filter(problem=problem)
        verdict = "Accepted"

        for testcase in testcases:
            result, output = run_code(lang, code, testcase.input)

            if result != "Success":
                verdict = result
                break
            elif output.strip() != testcase.expected_output.strip():
                verdict = "Wrong Answer"
                break

        # Save the submission
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
            'submitted_code': code
        })

    else:
        return redirect('problem_detail', problem_id=problem.id)




def run_code(language, code, input_data):
    #print("INPUT" + input_data)
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    with open(output_file_path, "w") as output_file:
        pass  # This will create an empty file

    if language == "c":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(["gcc", str(code_file_path), "-o", str(executable_path)])
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )
    
    elif language == "cpp":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(["g++", str(code_file_path), "-o", str(executable_path)])
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )

    elif language == "py":
        # Code for executing Python script
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python", str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )

    # Read the output from the output file
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    return output_data