import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";
import { api, ApiError } from "@/api/client";
import type { Grade } from "@/types";

interface FormValues {
  username: string;
  grade: Grade;
}

const grades: Grade[] = [10, 11, 12];

export default function Onboarding() {
  const setProfile = useAppStore((s) => s.setProfile);
  const navigate = useNavigate();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [composing, setComposing] = useState(false);
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    defaultValues: { username: "", grade: 10 },
  });

  const selectedGrade = watch("grade");

  const onSubmit = async (values: FormValues) => {
    setSubmitError(null);
    const username = values.username.trim();
    const grade = Number(values.grade) as Grade;
    try {
      const profile = await api.createUser({ username, grade });
      setProfile(profile.username, profile.grade, profile.userId);
      navigate("/discover", { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setSubmitError("Tên này đã được dùng. Hãy chọn tên khác.");
        return;
      }
      const message =
        err instanceof Error
          ? err.message
          : "Không tạo được tài khoản. Vui lòng thử lại.";
      setSubmitError(message);
    }
  };

  return (
    <section className="onboarding-screen">
      <div className="onboarding-card">
        <p className="kicker">Bắt đầu hành trình</p>
        <h1 className="headline-lg">Chào mừng đến với Vanver</h1>
        <p className="lead">
          Khám phá nhân vật văn học Việt Nam qua thẻ vuốt, trò chuyện và thử
          thách. Hãy giới thiệu bạn một chút.
        </p>
        <form className="onboarding-form" onSubmit={handleSubmit(onSubmit)}>
          <label className="field">
            <span>Tên hiển thị</span>
            <input
              autoComplete="off"
              placeholder="Ví dụ: Lan Anh"
              onCompositionStart={() => setComposing(true)}
              onCompositionEnd={() => setComposing(false)}
              {...register("username", {
                required: "Vui lòng nhập tên hiển thị",
                minLength: { value: 1, message: "Tên không được để trống" },
              })}
            />
            {errors.username && (
              <small className="error-text">{errors.username.message}</small>
            )}
          </label>

          <div className="field">
            <span>Khối lớp</span>
            <div className="grade-row">
              {grades.map((grade) => (
                <button
                  type="button"
                  key={grade}
                  className={`chip${selectedGrade === grade ? " active" : ""}`}
                  onClick={() => setValue("grade", grade)}
                >
                  Lớp {grade}
                </button>
              ))}
            </div>
          </div>

          {submitError && (
            <p className="error-text" role="alert">
              {submitError}
            </p>
          )}

          <button
            className="btn primary"
            type="submit"
            disabled={isSubmitting || composing}
          >
            {isSubmitting ? "Đang tạo tài khoản..." : "Vào khám phá"}
          </button>
        </form>
      </div>
    </section>
  );
}
