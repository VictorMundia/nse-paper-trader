// This imports useState to remember the quiz answers.
import { useState } from "react";
// This imports the icons used on the page.
import { BookOpen, CheckCircle2, ChevronDown, GraduationCap, XCircle } from "lucide-react";
// This imports the lesson text, glossary, and quiz questions.
import { GLOSSARY, LESSONS, QUIZ } from "../data/learnContent";

// This page teaches investing basics and lets students check their understanding.
export default function LearnPage() {
  // This maps question number -> chosen option, e.g. {0: 1, 2: 3}.
  const [answers, setAnswers] = useState({});
  // This counts correct answers among the questions answered so far.
  const correctCount = QUIZ.filter((item, index) => answers[index] === item.answer).length;

  // This returns the page layout.
  return (
    // This stacks the sections.
    <div className="space-y-8">
      {/* This is the title. */}
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold">
          <BookOpen className="h-7 w-7 text-emerald-600" aria-hidden="true" />
          Learn
        </h1>
        <p className="mt-1 text-slate-500">Short lessons on the Nairobi Securities Exchange and investing basics. Open any topic to read it.</p>
      </div>

      {/* These are the lessons; <details> opens and closes without any extra code. */}
      <section className="space-y-3">
        {LESSONS.map((lesson, index) => (
          <details key={lesson.id} className="group rounded-xl border border-slate-200 bg-white" open={index === 0}>
            {/* This is the clickable heading. */}
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-5">
              <div>
                <p className="font-semibold">
                  {index + 1}. {lesson.title}
                </p>
                <p className="text-sm text-slate-500">{lesson.summary}</p>
              </div>
              {/* The arrow turns when the lesson is open. */}
              <ChevronDown className="h-5 w-5 shrink-0 text-slate-400 transition group-open:rotate-180" aria-hidden="true" />
            </summary>
            {/* This is the lesson text. */}
            <div className="space-y-3 border-t border-slate-100 px-5 py-4 text-sm leading-relaxed text-slate-700">
              {lesson.paragraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </div>
          </details>
        ))}
      </section>

      {/* This is the self-check quiz. */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <GraduationCap className="h-6 w-6 text-sky-600" aria-hidden="true" />
            Check your understanding
          </h2>
          {/* This is the running score. */}
          <p className="text-sm text-slate-500">
            Score: <span className="font-semibold text-slate-900">{correctCount}</span> / {QUIZ.length}
          </p>
        </div>
        {/* This is the list of questions. */}
        <ol className="mt-4 space-y-6">
          {QUIZ.map((item, questionIndex) => {
            // This is the option the student picked, or undefined.
            const chosen = answers[questionIndex];
            // This is true once the question has been answered.
            const isAnswered = chosen !== undefined;
            // This returns one question.
            return (
              <li key={item.question}>
                <p className="font-medium">
                  {questionIndex + 1}. {item.question}
                </p>
                {/* These are the answer buttons. */}
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {item.options.map((option, optionIndex) => {
                    // After answering, the right option turns green and a wrong pick turns red.
                    const style = !isAnswered
                      ? "border-slate-200 hover:border-emerald-300 hover:bg-emerald-50"
                      : optionIndex === item.answer
                        ? "border-emerald-500 bg-emerald-50 text-emerald-800"
                        : optionIndex === chosen
                          ? "border-rose-400 bg-rose-50 text-rose-700"
                          : "border-slate-200 text-slate-400";
                    // This returns one option.
                    return (
                      <button
                        key={option}
                        type="button"
                        // Each question can be answered once, so the first choice counts.
                        disabled={isAnswered}
                        onClick={() => setAnswers({ ...answers, [questionIndex]: optionIndex })}
                        className={`rounded-lg border px-3 py-2 text-left text-sm ${style}`}
                      >
                        {option}
                      </button>
                    );
                  })}
                </div>
                {/* This shows the result and the explanation after answering. */}
                {isAnswered && (
                  <p className={`mt-2 flex items-start gap-2 text-sm ${chosen === item.answer ? "text-emerald-700" : "text-rose-700"}`}>
                    {chosen === item.answer ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" /> : <XCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />}
                    <span>
                      <span className="font-semibold">{chosen === item.answer ? "Correct. " : "Not quite. "}</span>
                      <span className="text-slate-700">{item.explanation}</span>
                    </span>
                  </p>
                )}
              </li>
            );
          })}
        </ol>
        {/* This lets the student try again once everything is answered. */}
        {Object.keys(answers).length === QUIZ.length && (
          <button type="button" onClick={() => setAnswers({})} className="mt-6 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50">
            Try again
          </button>
        )}
      </section>

      {/* This is the glossary. */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Glossary</h2>
        {/* A definition list pairs each term with its meaning. */}
        <dl className="mt-4 grid gap-x-8 gap-y-4 sm:grid-cols-2">
          {GLOSSARY.map((entry) => (
            <div key={entry.term}>
              <dt className="font-medium">{entry.term}</dt>
              <dd className="text-sm text-slate-600">{entry.definition}</dd>
            </div>
          ))}
        </dl>
      </section>

      {/* This is the disclaimer. */}
      <p className="text-xs text-slate-400">This content is for learning only and is not financial advice. Prices in this simulator are scraped from public data and may be delayed.</p>
    </div>
  );
}
