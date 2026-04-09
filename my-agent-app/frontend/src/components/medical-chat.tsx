"use client";

import {
  startTransition,
  useDeferredValue,
  useEffect,
  type KeyboardEvent,
  useMemo,
  useRef,
  useState,
} from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowUp,
  CalendarDays,
  ChevronDown,
  LoaderCircle,
  Phone,
  Plus,
  RefreshCw,
  Search,
  Sparkles,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
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

const VINMEC_HERO_IMAGE =
  "https://www.vinmec.com/static/uploads/anh_1_moi_b612967dee.jpg";

const UTILITY_LINKS = ["Tìm bác sĩ", "Chăm sóc khách hàng"];
const NAV_ITEMS = [
  "Chuyên khoa",
  "Hướng dẫn khách hàng",
  "Phát triển bền vững",
  "Về Vinmec",
  "Chuyên trang sức khỏe",
];

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
      return "Hỏi Vinmec AI về triệu chứng hoặc lịch khám";
  }
}

function summaryValue(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return "Chưa có";
  }
  return String(value);
}

function nextStepLabel(snapshot: Snapshot | null) {
  if (!snapshot) return "Đang khởi tạo tư vấn";

  const mapping: Record<string, string> = {
    facility: "Chọn cơ sở khám",
    doctor: "Chọn bác sĩ phụ trách",
    booking_date: "Chọn ngày khám",
    booking_time: "Chọn khung giờ phù hợp",
    name: "Nhập họ tên người khám",
    gender: "Chọn giới tính",
    phone_number: "Nhập số điện thoại",
    date_of_birth: "Nhập ngày sinh",
    email: "Điền email hoặc bỏ qua",
    booking_confirmation: "Xác nhận thông tin",
    otp_code: "Nhập OTP để hoàn tất",
    follow_up_answer: "Trả lời câu hỏi bổ sung",
  };

  return mapping[snapshot.pending_field ?? ""] ?? "Mô tả triệu chứng";
}

function bookingSchedule(snapshot: Snapshot | null) {
  const date = snapshot?.booking_context.booking_date;
  const time = snapshot?.booking_context.booking_time;

  if (!date && !time) return "Chưa có lịch hẹn";
  if (date && time) return `${date} • ${time}`;
  return date ?? time ?? "Chưa có lịch hẹn";
}

function formatConfidence(confidence: number | null | undefined) {
  if (!confidence) return "Đang chờ";
  return `${Math.round(confidence * 100)}%`;
}

function MessageBubble({ message }: { message: UiMessage }) {
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={cn("flex w-full", isAssistant ? "justify-start" : "justify-end")}
    >
      <div
        className={cn(
          "max-w-[82%] whitespace-pre-wrap rounded-[28px] px-4 py-3 text-sm leading-7 shadow-[0_20px_50px_rgba(15,23,42,0.07)]",
          isAssistant
            ? "rounded-tl-sm border border-slate-200 bg-white text-slate-800"
            : "rounded-tr-sm bg-[linear-gradient(135deg,#4b63ff,#7b8cff)] text-white",
        )}
      >
        {message.content}
      </div>
    </div>
  );
}

function VinmecLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-[radial-gradient(circle_at_35%_35%,#f8c36e,transparent_42%),radial-gradient(circle_at_55%_55%,#0f5caa,transparent_62%),linear-gradient(180deg,#f3c77f_0%,#b67b22_100%)] shadow-[0_12px_30px_rgba(17,88,155,0.18)]">
        <div className="absolute h-8 w-8 rounded-full border border-white/40" />
        <span className="text-xl font-semibold text-white">V</span>
      </div>
      <div className="leading-none">
        <p className="text-[2rem] font-semibold tracking-[0.14em] text-[#195fae]">
          VINMEC
        </p>
        <p className="mt-1 text-[10px] font-medium uppercase tracking-[0.26em] text-[#6e84a0]">
          Healthcare system
        </p>
      </div>
    </div>
  );
}

function FloatingDock({
  isAssistantOpen,
  onOpenAssistant,
}: {
  isAssistantOpen: boolean;
  onOpenAssistant: () => void;
}) {
  return (
    <div
      className={cn(
        "fixed bottom-5 right-4 z-40 flex flex-col items-center gap-3 transition-all duration-500 md:bottom-8 md:right-7",
        isAssistantOpen && "md:right-[28rem]",
      )}
    >
      <button
        type="button"
        onClick={() => {
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
        className="hidden size-14 items-center justify-center rounded-full border border-[#d6dde7] bg-white/92 text-[#7b8aa6] shadow-[0_18px_40px_rgba(15,23,42,0.09)] transition hover:-translate-y-1 hover:text-[#195fae] md:flex md:size-16"
        aria-label="Lên đầu trang"
      >
        <ArrowUp className="size-5" />
      </button>

      <a
        href="tel:1900232389"
        className="hidden size-14 items-center justify-center rounded-full bg-[#43a67f] text-white shadow-[0_18px_40px_rgba(67,166,127,0.28)] transition hover:-translate-y-1 md:flex md:size-16"
        aria-label="Gọi Vinmec"
      >
        <Phone className="size-5" />
      </a>

      <motion.button
        type="button"
        onClick={onOpenAssistant}
        whileHover={{ y: -4, scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        className="group relative flex size-14 items-center justify-center overflow-hidden rounded-full border border-white/55 bg-[linear-gradient(135deg,#5873ff_0%,#7ea0ff_55%,#aec5ff_100%)] text-white shadow-[0_24px_60px_rgba(88,115,255,0.35)] backdrop-blur md:size-16"
        aria-label={isAssistantOpen ? "Thu gọn Vinmec AI" : "Mở Vinmec AI"}
      >
        <motion.span
          aria-hidden
          className="absolute inset-y-0 left-[-35%] w-10 bg-white/28 blur-xl"
          animate={{ x: ["0%", "220%", "0%"] }}
          transition={{
            duration: 3.2,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
        <span className="relative flex size-10 items-center justify-center rounded-full bg-white/16 md:size-11">
          <Sparkles className="size-5" />
          <motion.span
            className="absolute inset-0 rounded-full border border-white/35"
            animate={{ scale: [1, 1.35, 1], opacity: [0.7, 0, 0.7] }}
            transition={{ duration: 2.2, repeat: Number.POSITIVE_INFINITY }}
          />
        </span>
      </motion.button>
    </div>
  );
}

function AssistantPanel({
  open,
  onClose,
  messages,
  input,
  onInputChange,
  onSend,
  isPending,
  loadingLabel,
  sessionId,
  quickReplies,
  pendingField,
  bootstrapError,
  onRestart,
}: {
  open: boolean;
  onClose: () => void;
  messages: UiMessage[];
  input: string;
  onInputChange: (value: string) => void;
  onSend: (rawValue?: string) => Promise<void>;
  isPending: boolean;
  loadingLabel: string;
  sessionId: string | null;
  quickReplies: string[];
  pendingField: string | null;
  bootstrapError: string | null;
  onRestart: () => Promise<void>;
}) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const hasUserMessage = messages.some((message) => message.role === "user");
  const welcomeMessage = messages[0]?.content;

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.nativeEvent.isComposing) {
      return;
    }

    if (event.ctrlKey || event.metaKey) {
      return;
    }

    event.preventDefault();
    if (!isPending && sessionId && input.trim()) {
      void onSend();
    }
  };

  useEffect(() => {
    if (!open) return;

    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isPending, open]);

  useEffect(() => {
    if (!open) return;

    const timeout = window.setTimeout(() => {
      inputRef.current?.focus();
    }, 180);

    return () => window.clearTimeout(timeout);
  }, [open]);

  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.button
            type="button"
            aria-label="Đóng trợ lý"
            className="fixed inset-0 z-40 bg-[#0c4582]/18 backdrop-blur-[2px]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 270, damping: 28 }}
            className="fixed inset-y-0 right-0 z-50 flex w-full max-w-[430px] flex-col border-l border-slate-200 bg-white shadow-[-18px_0_60px_rgba(15,23,42,0.18)]"
          >
            <div className="h-1.5 bg-[linear-gradient(90deg,#161616_0%,#5e73ff_36%,#96adff_100%)]" />

            <div className="flex items-center justify-between px-5 pb-4 pt-5">
              <div className="flex items-center gap-3">
                <span className="flex size-11 items-center justify-center rounded-full bg-[linear-gradient(135deg,#5e73ff,#a8b9ff)] text-white shadow-[0_14px_35px_rgba(94,115,255,0.28)]">
                  <Sparkles className="size-4" />
                </span>
                <div>
                  <p className="text-lg font-semibold tracking-tight text-[#7288ff]">
                    VinmecAI
                  </p>
                  <p className="text-xs text-slate-400">
                    {sessionId ? `Session ${sessionId.slice(0, 8)}` : "Đang kết nối"}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={onClose}
                className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                aria-label="Đóng"
              >
                <X className="size-4" />
              </button>
            </div>

            {bootstrapError ? (
              <div className="flex flex-1 flex-col items-center justify-center px-8 text-center">
                <AlertTriangle className="size-8 text-rose-600" />
                <h2 className="mt-5 text-2xl font-semibold text-slate-950">
                  Không thể kết nối
                </h2>
                <p className="mt-3 text-sm leading-7 text-slate-500">
                  {bootstrapError}
                </p>
                <Button
                  type="button"
                  onClick={() => {
                    void onRestart();
                  }}
                  className="mt-6 rounded-full bg-[#5f74ff] px-5 text-white hover:bg-[#4e64f2]"
                >
                  <RefreshCw className="size-4" />
                  Thử lại
                </Button>
              </div>
            ) : (
              <>
                <div className="flex-1 overflow-hidden">
                  {hasUserMessage ? (
                    <div
                      ref={scrollRef}
                      className="flex h-full flex-col gap-4 overflow-y-auto px-5 py-5"
                    >
                      {messages.map((message) => (
                        <MessageBubble key={message.id} message={message} />
                      ))}

                      {isPending ? (
                        <div className="flex justify-start">
                          <div className="inline-flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-[0_14px_35px_rgba(15,23,42,0.08)]">
                            <LoaderCircle className="size-4 animate-spin text-[#6176ff]" />
                            {loadingLabel}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <div className="flex h-full flex-col items-center justify-center px-8 text-center">
                      <div className="max-w-sm">
                        <p className="text-[2.15rem] font-semibold tracking-tight text-slate-950">
                          Mình có thể giúp gì cho bạn hôm nay?
                        </p>
                        <p className="mt-4 text-sm leading-7 text-slate-500">
                          {welcomeMessage ??
                            "Bạn có thể hỏi về triệu chứng, chuyên khoa phù hợp hoặc lịch khám tại Vinmec."}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="border-t border-slate-100 px-5 pb-5 pt-4">
                  {quickReplies.length ? (
                    <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
                      {quickReplies.map((reply) => (
                        <button
                          key={reply}
                          type="button"
                          onClick={() => {
                            void onSend(reply);
                          }}
                          disabled={isPending}
                          className="shrink-0 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-600 transition hover:border-[#7b8cff] hover:text-slate-950"
                        >
                          {reply}
                        </button>
                      ))}
                    </div>
                  ) : null}

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void onSend();
                    }}
                    className="rounded-[2rem] border border-slate-200 bg-white px-3 py-2 shadow-[0_18px_40px_rgba(15,23,42,0.05)]"
                  >
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        className="flex size-10 items-center justify-center rounded-full text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                        aria-label="Mở thêm tùy chọn"
                      >
                        <Plus className="size-5" />
                      </button>

                      <Textarea
                        ref={inputRef}
                        value={input}
                        onChange={(event) => onInputChange(event.target.value)}
                        onKeyDown={handleComposerKeyDown}
                        placeholder={pendingPlaceholder(pendingField)}
                        disabled={isPending || !sessionId}
                        rows={1}
                        className="max-h-36 min-h-[3rem] resize-none border-0 bg-transparent px-0 py-3 text-base leading-6 text-slate-950 shadow-none focus-visible:ring-0"
                      />

                      <button
                        type="submit"
                        disabled={isPending || !sessionId || !input.trim()}
                        className="flex size-10 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition hover:bg-[#6579ff] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                        aria-label="Gửi"
                      >
                        <ArrowUp className="size-4" />
                      </button>
                    </div>
                  </form>

                  <p className="mt-3 text-center text-xs leading-6 text-slate-400">
                    Enter để gửi, Ctrl+Enter hoặc Cmd+Enter để xuống dòng. VinmecAI có thể mắc lỗi. Hãy kiểm tra lại thông tin quan trọng.
                  </p>
                </div>
              </>
            )}
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
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
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  const deferredQuickReplies = useDeferredValue(quickReplies);
  const visibleQuickReplies = deferredQuickReplies.slice(0, 5);

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
    <>
      <main className="min-h-[100dvh] bg-[#f7fafc] text-slate-900">
        <section className="bg-[linear-gradient(90deg,#1169a8_0%,#2478b6_52%,#3d88bf_100%)] text-white">
          <div className="mx-auto flex max-w-[1440px] items-center justify-end gap-8 px-4 py-3 text-sm md:px-6 lg:px-8">
            {UTILITY_LINKS.map((item) => (
              <a
                key={item}
                href="#"
                className="transition hover:text-white/80"
              >
                {item}
              </a>
            ))}
          </div>
        </section>

        <header className="border-b border-[#dbe7ef] bg-white/96 backdrop-blur">
          <div className="mx-auto flex max-w-[1440px] flex-col gap-4 px-4 py-4 md:px-6 lg:px-8">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
              <VinmecLogo />

              <div className="flex flex-1 items-center justify-end gap-3">
                <div className="hidden min-w-[320px] max-w-[460px] flex-1 items-center gap-3 rounded-2xl border border-[#d5e1eb] px-4 py-3 text-slate-400 lg:flex">
                  <Search className="size-5 text-[#2b6fbe]" />
                  <span className="text-lg text-slate-400">Tìm kiếm...</span>
                </div>

                <button
                  type="button"
                  className="flex size-11 items-center justify-center rounded-2xl border border-[#d5e1eb] text-[#2b6fbe]"
                  aria-label="Lịch"
                >
                  <CalendarDays className="size-5" />
                </button>

                <button
                  type="button"
                  className="flex h-11 items-center gap-2 rounded-2xl border border-[#d5e1eb] px-3 text-sm text-slate-600"
                >
                  <span className="text-lg">VN</span>
                  <ChevronDown className="size-4 text-slate-400" />
                </button>
              </div>
            </div>

            <nav className="hidden items-center justify-center gap-10 border-t border-[#edf2f6] pt-5 text-[1.05rem] text-slate-700 lg:flex">
              {NAV_ITEMS.map((item) => (
                <a key={item} href="#" className="transition hover:text-[#1d63af]">
                  {item}
                </a>
              ))}
            </nav>
          </div>
        </header>

        <section className="mx-auto max-w-[1440px] px-4 pb-16 pt-8 md:px-6 lg:px-8">
          <div className="relative min-h-[760px] overflow-hidden rounded-[30px] bg-white">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(182,207,233,0.3),transparent_24%),radial-gradient(circle_at_bottom_right,rgba(211,230,221,0.28),transparent_22%)]" />
            <div className="pointer-events-none absolute left-7 top-20 hidden size-12 rounded-full bg-[#edf4fb] shadow-[0_0_0_14px_rgba(237,244,251,0.45)] lg:block" />
            <div className="pointer-events-none absolute right-12 top-14 hidden h-28 w-28 rounded-full border-[18px] border-[#eff5d8] opacity-70 lg:block" />
            <div className="pointer-events-none absolute bottom-10 left-10 hidden h-24 w-24 rounded-full bg-[#eef6d8]/75 blur-2xl lg:block" />

            <div className="relative flex min-h-[760px] items-start justify-center px-4 pt-8 md:px-6">
              <img
                src={VINMEC_HERO_IMAGE}
                alt="Vinmec campaign collage"
                className="w-full max-w-[1120px] object-contain"
              />
            </div>
          </div>
        </section>
      </main>

      <FloatingDock
        isAssistantOpen={isAssistantOpen}
        onOpenAssistant={() => setIsAssistantOpen((prev) => !prev)}
      />

      <AssistantPanel
        open={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        messages={messages}
        input={input}
        onInputChange={setInput}
        onSend={handleSend}
        isPending={isPending}
        loadingLabel={loadingLabel}
        sessionId={sessionId}
        quickReplies={visibleQuickReplies}
        pendingField={snapshot?.pending_field ?? null}
        bootstrapError={bootstrapError}
        onRestart={handleRestart}
      />
    </>
  );
}
