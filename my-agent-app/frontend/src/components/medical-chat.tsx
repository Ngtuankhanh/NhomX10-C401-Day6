"use client";

import { startTransition, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  CircleDotDashed,
  ClipboardList,
  LoaderCircle,
  MapPin,
  RefreshCw,
  SendHorizontal,
  ShieldAlert,
  Stethoscope,
  UserRound,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";


type ApiRole = "assistant" | "user";

type ApiMessage = {
  role: ApiRole;
  content: string;
  created_at: string;
};

type ChatStatus = {
  code: string;
  label: string;
};

type Snapshot = {
  conversation_state: string;
  pending_field: string | null;
  triage_attempt_count: number;
  symptom_summary: string | null;
  specialty_assessment: {
    speciality_id: number | null;
    speciality_name: string | null;
    description: string | null;
    confidence: number | null;
    question: string | null;
    matched_symptoms: string[];
    fallback_used: boolean;
    agent_b_status: string;
  };
  booking_context: {
    place_id: number | null;
    facility_name: string | null;
    geo_division: string | null;
    speciality_id: number | null;
    speciality_name: string | null;
    doctor_id: number | null;
    professional_id: number | null;
    doctor_name: string | null;
    doctor_ad: string | null;
    booking_date: string | null;
    booking_time: string | null;
  };
  patient_info: {
    name: string | null;
    gender: number | null;
    phone_number: string | null;
    date_of_birth: string | null;
    email: string | null;
    inquiry_info: string | null;
  };
  booking_verification: {
    verif_id: string | null;
    masked_username: string | null;
    otp_required: boolean;
    booking_id: number | null;
  };
  failure_state: {
    agent_b_failures: number;
    slot_lookup_failures: number;
    booking_failures: number;
    last_error_code: string | null;
  };
  booking_mode: string;
};

type ChatApiResponse = {
  session_id: string;
  assistant_message: ApiMessage;
  conversation_state: string;
  status: ChatStatus;
  quick_replies: string[];
  snapshot: Snapshot;
};

type UiMessage = {
  id: string;
  role: ApiRole;
  content: string;
};


const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:2024";


function buildMessageId(prefix: string) {
  return `${prefix}-${crypto.randomUUID()}`;
}

async function createSession(): Promise<ChatApiResponse> {
  const response = await fetch(`${BACKEND_URL}/api/chat/session`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Không thể khởi tạo phiên chat.");
  }
  return response.json();
}

async function sendMessage(
  sessionId: string,
  message: string,
): Promise<ChatApiResponse> {
  const response = await fetch(`${BACKEND_URL}/api/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Không thể gửi tin nhắn tới trợ lý.");
  }

  return response.json();
}

function statusTone(code: string) {
  switch (code) {
    case "recovering_from_error":
      return "bg-amber-100 text-amber-900 border-amber-200";
    case "waiting_for_otp":
      return "bg-blue-100 text-blue-900 border-blue-200";
    case "idle":
      return "bg-emerald-100 text-emerald-900 border-emerald-200";
    default:
      return "bg-slate-100 text-slate-900 border-slate-200";
  }
}

function pendingPlaceholder(pendingField: string | null) {
  switch (pendingField) {
    case "facility":
      return "Nhập tên cơ sở hoặc chọn nhanh bên dưới";
    case "doctor":
      return "Nhập tên bác sĩ hoặc chọn nhanh";
    case "booking_date":
      return "Ví dụ: 12/04/2026";
    case "booking_time":
      return "Ví dụ: 09:20";
    case "name":
      return "Nhập họ và tên";
    case "gender":
      return "Nam hoặc Nữ";
    case "phone_number":
      return "Nhập số điện thoại";
    case "date_of_birth":
      return "Ví dụ: 1996-06-13";
    case "email":
      return "Nhập email hoặc gõ 'bỏ qua'";
    case "booking_confirmation":
      return "Gõ xác nhận hoặc sửa thông tin";
    case "otp_code":
      return "Nhập mã OTP 6 số";
    default:
      return "Mô tả triệu chứng hoặc nhập phản hồi";
  }
}

function summaryValue(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return "Chưa có";
  }
  return String(value);
}

function nextStepLabel(snapshot: Snapshot | null) {
  if (!snapshot) return "Chờ phiên chat khởi tạo";

  const mapping: Record<string, string> = {
    facility: "Chọn cơ sở khám",
    doctor: "Chọn bác sĩ",
    booking_date: "Chọn ngày khám",
    booking_time: "Chọn giờ khám",
    name: "Nhập họ tên",
    gender: "Chọn giới tính",
    phone_number: "Nhập số điện thoại",
    date_of_birth: "Nhập ngày sinh",
    email: "Nhập email hoặc bỏ qua",
    booking_confirmation: "Xác nhận thông tin",
    otp_code: "Nhập OTP",
    follow_up_answer: "Trả lời câu hỏi bổ sung",
  };

  return mapping[snapshot.pending_field ?? ""] ?? "Mô tả triệu chứng";
}

function MessageBubble({ message }: { message: UiMessage }) {
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={cn(
        "flex w-full",
        isAssistant ? "justify-start" : "justify-end",
      )}
    >
      <div
        className={cn(
          "max-w-[88%] rounded-3xl px-4 py-3 text-sm leading-7 shadow-sm whitespace-pre-wrap",
          isAssistant
            ? "bg-white text-slate-900 rounded-tl-md border border-slate-200"
            : "bg-[linear-gradient(135deg,#0f766e,#115e59)] text-white rounded-tr-md",
        )}
      >
        {message.content}
      </div>
    </div>
  );
}

function SummaryPanel({
  snapshot,
  status,
}: {
  snapshot: Snapshot | null;
  status: ChatStatus | null;
}) {
  const genderLabel =
    snapshot?.patient_info.gender === 1
      ? "Nam"
      : snapshot?.patient_info.gender === 2
        ? "Nữ"
        : "Chưa có";

  return (
    <div className="flex flex-col gap-4">
      <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-base text-slate-950">
            <CircleDotDashed className="size-4 text-teal-700" />
            Trạng thái phiên
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-700">
          <div
            className={cn(
              "inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium",
              statusTone(status?.code ?? "idle"),
            )}
          >
            <span className="size-2 rounded-full bg-current opacity-80" />
            {status?.label ?? "Sẵn sàng hỗ trợ"}
          </div>
          <div className="rounded-2xl bg-slate-50 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Bước kế tiếp
            </p>
            <p className="mt-2 font-medium text-slate-900">
              {nextStepLabel(snapshot)}
            </p>
          </div>
          <div className="rounded-2xl bg-amber-50 px-4 py-3 text-amber-950">
            <div className="flex items-start gap-3">
              <ShieldAlert className="mt-0.5 size-4 shrink-0" />
              <p className="text-sm leading-6">
                Chatbot chỉ gợi ý chuyên khoa và hỗ trợ đặt lịch, không thay thế
                chẩn đoán của bác sĩ.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-base text-slate-950">
            <Stethoscope className="size-4 text-teal-700" />
            Gợi ý chuyên khoa
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-700">
          <div className="rounded-2xl bg-slate-50 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Chuyên khoa
            </p>
            <p className="mt-2 font-medium text-slate-950">
              {summaryValue(snapshot?.specialty_assessment.speciality_name)}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Độ tin cậy
              </p>
              <p className="mt-2 font-medium text-slate-950">
                {snapshot?.specialty_assessment.confidence
                  ? `${Math.round(
                      snapshot.specialty_assessment.confidence * 100,
                    )}%`
                  : "Chưa có"}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Agent B
              </p>
              <p className="mt-2 font-medium text-slate-950">
                {snapshot?.specialty_assessment.agent_b_status === "fallback"
                  ? "Placeholder, đang dùng fallback"
                  : "Chưa chạy"}
              </p>
            </div>
          </div>
          <div className="rounded-2xl bg-slate-50 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Tóm tắt triệu chứng
            </p>
            <p className="mt-2 leading-6 text-slate-900">
              {summaryValue(snapshot?.symptom_summary)}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-base text-slate-950">
            <CalendarDays className="size-4 text-teal-700" />
            Tiến độ đặt lịch
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-700">
          <div className="grid gap-3">
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Cơ sở
              </p>
              <p className="mt-2 text-slate-950">
                {summaryValue(snapshot?.booking_context.facility_name)}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Bác sĩ
              </p>
              <p className="mt-2 text-slate-950">
                {summaryValue(snapshot?.booking_context.doctor_name)}
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Ngày khám
                </p>
                <p className="mt-2 text-slate-950">
                  {summaryValue(snapshot?.booking_context.booking_date)}
                </p>
              </div>
              <div className="rounded-2xl bg-slate-50 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Giờ khám
                </p>
                <p className="mt-2 text-slate-950">
                  {summaryValue(snapshot?.booking_context.booking_time)}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-base text-slate-950">
            <UserRound className="size-4 text-teal-700" />
            Thông tin người khám
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-700">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Họ tên
              </p>
              <p className="mt-2 text-slate-950">
                {summaryValue(snapshot?.patient_info.name)}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Giới tính
              </p>
              <p className="mt-2 text-slate-950">{genderLabel}</p>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Số điện thoại
              </p>
              <p className="mt-2 text-slate-950">
                {summaryValue(snapshot?.patient_info.phone_number)}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-50 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Ngày sinh
              </p>
              <p className="mt-2 text-slate-950">
                {summaryValue(snapshot?.patient_info.date_of_birth)}
              </p>
            </div>
          </div>
          <div className="rounded-2xl bg-slate-50 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Email
            </p>
            <p className="mt-2 text-slate-950">
              {summaryValue(snapshot?.patient_info.email)}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function MedicalChat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [quickReplies, setQuickReplies] = useState<string[]>([]);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [status, setStatus] = useState<ChatStatus | null>(null);
  const [input, setInput] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [bootstrapError, setBootstrapError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const deferredQuickReplies = useMemo(() => quickReplies.slice(0, 6), [quickReplies]);

  useEffect(() => {
    let cancelled = false;

    createSession()
      .then((payload) => {
        if (cancelled) return;

        startTransition(() => {
          setSessionId(payload.session_id);
          setMessages([
            {
              id: buildMessageId("assistant"),
              role: "assistant",
              content: payload.assistant_message.content,
            },
          ]);
          setQuickReplies(payload.quick_replies);
          setSnapshot(payload.snapshot);
          setStatus(payload.status);
        });
      })
      .catch((error: Error) => {
        if (cancelled) return;
        setBootstrapError(error.message);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isPending]);

  const loadingLabel = useMemo(() => {
    if (!snapshot) return "Đang khởi tạo phiên chat...";

    if (snapshot.pending_field === "otp_code") {
      return "Đang xác nhận lịch hẹn...";
    }
    if (
      snapshot.pending_field === "facility" ||
      snapshot.pending_field === "doctor" ||
      snapshot.pending_field === "booking_date" ||
      snapshot.pending_field === "booking_time"
    ) {
      return "Đang tìm lịch phù hợp...";
    }
    if (snapshot.pending_field === "booking_confirmation") {
      return "Đang gửi yêu cầu đặt lịch...";
    }
    return "Đang phân tích triệu chứng...";
  }, [snapshot]);

  const handleSend = async (rawValue?: string) => {
    const message = (rawValue ?? input).trim();
    if (!message || !sessionId || isPending) return;

    const optimisticUserMessage: UiMessage = {
      id: buildMessageId("user"),
      role: "user",
      content: message,
    };

    startTransition(() => {
      setMessages((prev) => [...prev, optimisticUserMessage]);
      setInput("");
      setIsPending(true);
    });

    try {
      const payload = await sendMessage(sessionId, message);
      startTransition(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: buildMessageId("assistant"),
            role: "assistant",
            content: payload.assistant_message.content,
          },
        ]);
        setQuickReplies(payload.quick_replies);
        setSnapshot(payload.snapshot);
        setStatus(payload.status);
        setIsPending(false);
      });
    } catch (error) {
      startTransition(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: buildMessageId("assistant"),
            role: "assistant",
            content:
              error instanceof Error
                ? error.message
                : "Không thể gửi tin nhắn tới backend.",
          },
        ]);
        setIsPending(false);
      });
    }
  };

  const handleRestart = async () => {
    setBootstrapError(null);
    setIsPending(true);
    try {
      const payload = await createSession();
      startTransition(() => {
        setSessionId(payload.session_id);
        setMessages([
          {
            id: buildMessageId("assistant"),
            role: "assistant",
            content: payload.assistant_message.content,
          },
        ]);
        setQuickReplies(payload.quick_replies);
        setSnapshot(payload.snapshot);
        setStatus(payload.status);
        setInput("");
        setIsPending(false);
      });
    } catch (error) {
      setBootstrapError(
        error instanceof Error ? error.message : "Không thể tạo phiên mới.",
      );
      setIsPending(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#d8f3f0,transparent_26%),radial-gradient(circle_at_bottom_right,#fde68a,transparent_24%),linear-gradient(180deg,#f8fafc_0%,#eef6f5_100%)] px-4 py-6 text-slate-950 md:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <section className="grid gap-6 lg:grid-cols-[1.45fr_0.8fr]">
          <Card className="overflow-hidden border-white/70 bg-white/85 shadow-[0_30px_120px_rgba(15,23,42,0.10)] backdrop-blur">
            <CardHeader className="border-b border-slate-200/80 bg-[linear-gradient(135deg,#f7fffe,#eef8f6)] pb-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-teal-900">
                    <Stethoscope className="size-3.5" />
                    Trợ lý đặt lịch y tế
                  </div>
                  <div>
                    <h1 className="max-w-2xl text-2xl font-semibold tracking-tight text-slate-950 md:text-3xl">
                      Chatbot gợi ý chuyên khoa và hỗ trợ đặt lịch khám
                    </h1>
                    <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600 md:text-base">
                      Luồng hiện tại đã triển khai toàn bộ FE và Agent A. Agent B
                      đang ở chế độ placeholder nên hệ thống sẽ tự fallback sang
                      bộ phân loại dựa trên dữ liệu tri thức trong backend.
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium",
                      statusTone(status?.code ?? "idle"),
                    )}
                  >
                    <span className="size-2 rounded-full bg-current opacity-80" />
                    {status?.label ?? "Đang sẵn sàng"}
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    className="rounded-full"
                    onClick={handleRestart}
                    disabled={isPending}
                  >
                    <RefreshCw className="size-4" />
                    Phiên mới
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              {bootstrapError ? (
                <div className="flex min-h-[640px] items-center justify-center p-8">
                  <div className="max-w-md rounded-3xl border border-rose-200 bg-rose-50 p-6 text-center text-rose-950">
                    <AlertTriangle className="mx-auto size-8" />
                    <h2 className="mt-4 text-lg font-semibold">Không thể kết nối backend</h2>
                    <p className="mt-2 text-sm leading-6">{bootstrapError}</p>
                    <Button className="mt-5 rounded-full" onClick={handleRestart}>
                      Thử lại
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="grid min-h-[640px] grid-rows-[1fr_auto]">
                  <div
                    ref={scrollRef}
                    className="space-y-4 overflow-y-auto px-4 py-5 md:px-6"
                  >
                    {messages.map((message) => (
                      <MessageBubble key={message.id} message={message} />
                    ))}

                    {isPending ? (
                      <div className="flex justify-start">
                        <div className="inline-flex items-center gap-3 rounded-3xl rounded-tl-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm">
                          <LoaderCircle className="size-4 animate-spin text-teal-700" />
                          {loadingLabel}
                        </div>
                      </div>
                    ) : null}
                  </div>

                  <div className="border-t border-slate-200/80 bg-white/90 px-4 py-4 md:px-6">
                    {deferredQuickReplies.length ? (
                      <div className="mb-4 flex flex-wrap gap-2">
                        {deferredQuickReplies.map((reply) => (
                          <button
                            key={reply}
                            type="button"
                            className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-left text-sm text-slate-700 transition hover:border-teal-300 hover:bg-teal-50 hover:text-teal-950"
                            onClick={() => {
                              void handleSend(reply);
                            }}
                            disabled={isPending}
                          >
                            {reply}
                          </button>
                        ))}
                      </div>
                    ) : null}

                    <form
                      className="flex flex-col gap-3 md:flex-row"
                      onSubmit={(event) => {
                        event.preventDefault();
                        void handleSend();
                      }}
                    >
                      <Input
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        placeholder={pendingPlaceholder(snapshot?.pending_field ?? null)}
                        className="h-12 rounded-full border-slate-200 bg-slate-50 px-5"
                        disabled={isPending || !sessionId}
                      />
                      <Button
                        type="submit"
                        className="h-12 rounded-full bg-[linear-gradient(135deg,#0f766e,#115e59)] px-5 text-white hover:opacity-95"
                        disabled={isPending || !sessionId || !input.trim()}
                      >
                        <SendHorizontal className="size-4" />
                        Gửi
                      </Button>
                    </form>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <SummaryPanel snapshot={snapshot} status={status} />
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
            <CardContent className="flex items-start gap-4 p-5">
              <MapPin className="mt-1 size-5 text-teal-700" />
              <div>
                <p className="text-sm font-semibold text-slate-950">Flow booking theo từng bước</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Agent A sẽ hỏi lần lượt cơ sở, bác sĩ, ngày, giờ rồi mới sang
                  phần thông tin người khám để giảm lỗi dữ liệu.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
            <CardContent className="flex items-start gap-4 p-5">
              <ClipboardList className="mt-1 size-5 text-teal-700" />
              <div>
                <p className="text-sm font-semibold text-slate-950">Fallback rõ ràng</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Nếu Agent B chưa sẵn sàng, hệ thống vẫn phân loại bằng dữ liệu
                  nội bộ và hiển thị trạng thái fallback rõ ràng trong UI.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
            <CardContent className="flex items-start gap-4 p-5">
              <CheckCircle2 className="mt-1 size-5 text-teal-700" />
              <div>
                <p className="text-sm font-semibold text-slate-950">OTP demo để test end-to-end</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Booking đang ở chế độ mock an toàn. Bạn có thể dùng OTP mẫu
                  `123456` để đi xuyên suốt toàn bộ flow FE và Agent A.
                </p>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
}
