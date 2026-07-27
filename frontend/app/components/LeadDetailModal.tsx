"use client";
import { api, resolveLeadImageUrl } from '@/lib/api';

import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import ChatPanel from "./ChatPanel";
import {
  X,
  Save,
  MapPin,
  Phone,
  Mail,
  Globe,
  ExternalLink,
  Clock,
  MessageSquare,
  Loader2,
  User,
  Sparkles,
  Flame,
  Star,
  Check,
  Image as ImageIcon,
  AlertCircle,
  Building2,
  Building,
  ScrollText,
  Briefcase,
  ShieldAlert
} from "lucide-react";

interface Lead {
  id?: string;
  name: string;
  address: string;
  score: number;
  email?: string;
  social_url?: string;
  booking_url?: string;
  phone?: string;
  responsavel_contato?: string;
  responsavel_nome?: string;
  website?: string;
  vision_image_url?: string;
  interaction_notes?: string;
  return_date?: string;
  contact_status?: string;
  is_favorite?: boolean | number;
  intencao_ativa?: boolean | number;
  resumo_sinal?: string;
  link_fonte?: string;
  score_urgencia?: number;
  categoria_demanda?: string;
  pilar?: string;
  crm_notes?: string;
  crm_response?: string;
}

interface Props {
  lead: Lead;
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  readOnly?: boolean;
}

export default function LeadDetailModal({ lead, isOpen, onClose, onSave, readOnly = false }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  const leadId = lead.id || lead.name.toLowerCase().replace(/\s+/g, "_").replace(/\//g, "-");

  const [notes, setNotes] = useState(lead.interaction_notes || "");
  const [returnDate, setReturnDate] = useState(lead.return_date || "");
  const [status, setStatus] = useState(lead.contact_status || "Aguardando Abordagem");
  const [saving, setSaving] = useState(false);
  const [crmNotes, setCrmNotes] = useState(lead.crm_notes || "");
  const [crmResponse, setCrmResponse] = useState(lead.crm_response || "");
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Estado para correção de fachada
  const [fachadaUrl, setFachadaUrl] = useState(lead.vision_image_url || "");
  const [fachadaInputVisible, setFachadaInputVisible] = useState(false);
  const [fachadaPreview, setFachadaPreview] = useState(lead.vision_image_url || "");
  const [fachadaError, setFachadaError] = useState(false);

  useEffect(() => {
    setNotes(lead.interaction_notes || "");
    setReturnDate(lead.return_date || "");
    setStatus(lead.contact_status || "Aguardando Abordagem");
    setCrmNotes(lead.crm_notes || "");
    setCrmResponse(lead.crm_response || "");
    if (typeof window !== "undefined") {
      try {
        setCurrentUser(JSON.parse(localStorage.getItem("currentUser") || "{}"));
      } catch {}
    }
  }, [lead]);

  // Normalização do telefone para WhatsApp
  const phoneRaw = lead.phone || lead.responsavel_contato || "";
  const phoneNumbersOnly = phoneRaw.replace(/\D/g, "");

  let whatsappUrl = "";
  if (phoneNumbersOnly) {
    let formattedNum = phoneNumbersOnly;
    if (formattedNum.length === 10 || formattedNum.length === 11) {
      formattedNum = "55" + formattedNum;
    }
    whatsappUrl = `https://wa.me/${formattedNum}`;
  }

  async function handleSave() {
    setSaving(true);
    try {
      const body = {
        notes,
        return_date: returnDate || null,
        contact_status: status,
        vision_image_url: fachadaPreview || null
      };
      const res = await api.interaction(leadId, body);
      if (res.ok) {
        onSave();
        onClose();
      } else {
        alert("Erro ao salvar dados comercial.");
      }
    } catch (error) {
      console.error("Erro ao salvar interação no CRM:", error);
      alert("Erro de conexão.");
    } finally {
      setSaving(false);
    }
  }

  function handleApplyFachada() {
    setFachadaPreview(fachadaUrl);
    setFachadaError(false);
    setFachadaInputVisible(false);
  }

  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[99999] flex items-start md:items-center justify-center overflow-y-auto md:overflow-hidden">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/80 backdrop-blur-md"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="bg-slate-950/95 backdrop-blur-xl border-0 w-screen h-screen fixed inset-0 max-w-none rounded-none p-4 sm:p-6 md:p-10 lg:p-14 shadow-2xl relative z-10 flex flex-col md:flex-row gap-6 md:gap-10 overflow-y-auto md:overflow-hidden"
          >
            {/* Warning Banner for ReadOnly */}
            {readOnly && (
              <div className="fixed top-0 left-0 right-0 bg-yellow-400/10 border-b border-yellow-400/20 text-yellow-400 text-[10px] font-black uppercase tracking-[0.2em] py-2.5 px-6 flex items-center gap-2 z-[25]">
                <ShieldAlert size={14} className="animate-pulse" />
                <span>Modo de Visualização (Outro Vendedor Favoritou / Somente Leitura)</span>
              </div>
            )}

            {/* Close Button */}
            <button
              onClick={onClose}
              className="fixed top-4 right-4 md:top-6 md:right-6 lg:top-10 lg:right-10 p-3 rounded-full bg-slate-900 border border-white/10 text-slate-400 hover:text-white hover:bg-slate-800 transition-all z-35 flex items-center gap-2 shadow-lg shadow-black/50"
              title="Sair do CRM"
            >
              <span className="text-[10px] font-black uppercase tracking-widest pl-1 hidden sm:inline">Sair do CRM</span>
              <X size={16} />
            </button>

            {/* ── Coluna 1: Informações do Lead ── */}
            <div className={`flex-1 flex flex-col gap-3 sm:gap-4 md:border-r md:border-white/5 md:pr-6 md:overflow-y-auto md:max-h-full pr-2 scrollbar-thin ${readOnly ? "pt-10 md:pt-6" : "pt-8 md:pt-0"}`}>

              {/* ── Bloco 1: Cabeçalho ── */}
              <div>
                {/* Badges */}
                <div className="flex items-center gap-1.5 mb-2 flex-wrap">
                  <span className="bg-yellow-400/10 text-yellow-400 text-[9px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-full border border-yellow-400/20 flex items-center gap-1">
                    <Sparkles size={9} /> Lead Radar
                  </span>
                  {lead.is_favorite ? (
                    <span className="bg-rose-500/10 text-rose-400 text-[9px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-full border border-rose-500/20 flex items-center gap-1">
                      <Flame size={9} className="fill-rose-400" /> Lead Quente
                    </span>
                  ) : null}
                  {(lead.pilar || 'A') === 'A' && (
                    <span className="bg-blue-500/10 text-blue-400 text-[9px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-full border border-blue-500/20 flex items-center gap-1">
                      <Building2 size={9} /> Pilar A: Condomínios
                    </span>
                  )}
                  {lead.pilar === 'B' && (
                    <span className="bg-emerald-500/10 text-emerald-400 text-[9px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
                      <Building size={9} /> Pilar B: Grande Porte
                    </span>
                  )}
                  {lead.pilar === 'C' && (
                    <span className="bg-amber-500/10 text-amber-400 text-[9px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-full border border-amber-500/20 flex items-center gap-1">
                      <ScrollText size={9} /> Pilar C: Editais
                    </span>
                  )}
                </div>
                {/* Nome + Endereço */}
                <h2 className="text-lg sm:text-xl lg:text-2xl font-black text-white uppercase tracking-tight leading-tight pr-8">
                  {lead.name}
                </h2>
                <p className="text-slate-400 text-xs flex items-center gap-1.5 mt-1.5 font-medium break-words">
                  <MapPin size={12} className="text-yellow-400 shrink-0" />
                  <span className="break-words">{lead.address}</span>
                </p>
              </div>

              {/* ── Bloco 2: Contato Rápido (fachada + telefone + ações) ── */}
              <div className="flex gap-3">
                {/* Thumbnail da Fachada */}
                <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-xl overflow-hidden bg-slate-950 border border-white/5 relative shrink-0">
                  <img
                    src={resolveLeadImageUrl(fachadaPreview)}
                    className="w-full h-full object-cover"
                    alt="Fachada"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=600&auto=format&fit=crop&q=80";
                    }}
                  />
                  {!readOnly && (
                    <button
                      onClick={() => setFachadaInputVisible(v => !v)}
                      className="absolute bottom-1 right-1 bg-slate-900/90 hover:bg-yellow-400 hover:text-slate-900 text-slate-300 text-[8px] font-black uppercase tracking-widest px-1.5 py-1 rounded-lg border border-white/10 transition-all flex items-center gap-1 backdrop-blur-sm"
                    >
                      <ImageIcon size={8} /> Foto
                    </button>
                  )}
                </div>

                {/* Info de Contato */}
                <div className="flex-1 flex flex-col justify-between min-w-0">
                  {/* Telefone */}
                  <div>
                    <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1 mb-0.5">
                      <Phone size={10} className="text-yellow-400" /> Telefone
                    </span>
                    <p className="text-sm sm:text-base font-black text-yellow-400 font-mono break-all leading-tight">
                      {phoneRaw || 'Não cadastrado'}
                    </p>
                  </div>
                  {/* Botões de Ação */}
                  <div className="flex gap-2 mt-2">
                    {whatsappUrl ? (
                      <a
                        href={whatsappUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="flex-1 bg-yellow-400 hover:bg-yellow-300 text-slate-900 font-black py-2 px-2 rounded-xl flex items-center justify-center gap-1.5 transition-all text-[10px] uppercase tracking-widest shadow-lg shadow-yellow-400/10 hover:scale-[1.02] active:scale-95"
                      >
                        <Phone size={12} className="fill-slate-900" /> WhatsApp
                      </a>
                    ) : (
                      <button disabled className="flex-1 bg-slate-800 text-slate-600 font-black py-2 px-2 rounded-xl flex items-center justify-center gap-1.5 text-[10px] uppercase tracking-widest opacity-40 cursor-not-allowed">
                        <Phone size={12} /> Sem WhatsApp
                      </button>
                    )}
                    {lead.email && lead.email !== "N/D" ? (
                      <a
                        href={`mailto:${lead.email}`}
                        className="flex-1 bg-slate-800 hover:bg-slate-700 border border-white/5 hover:border-white/10 text-white font-black py-2 px-2 rounded-xl flex items-center justify-center gap-1.5 transition-all text-[10px] uppercase tracking-widest hover:scale-[1.02] active:scale-95"
                      >
                        <Mail size={12} className="text-yellow-400" /> E-mail
                      </a>
                    ) : (
                      <button disabled className="flex-1 bg-slate-800 text-slate-600 font-black py-2 px-2 rounded-xl flex items-center justify-center gap-1.5 text-[10px] uppercase tracking-widest opacity-40 cursor-not-allowed">
                        <Mail size={12} /> Sem E-mail
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Correção de Fachada (colapsável) */}
              <AnimatePresence>
                {fachadaInputVisible && !readOnly && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="flex gap-2 bg-slate-950 border border-yellow-400/30 rounded-xl p-3">
                      <div className="flex-1 min-w-0">
                        <label className="text-[9px] font-black text-yellow-400 uppercase tracking-widest block mb-1">
                          URL da foto da fachada
                        </label>
                        <input
                          type="url"
                          value={fachadaUrl}
                          onChange={e => { setFachadaUrl(e.target.value); setFachadaError(false); }}
                          placeholder="https://exemplo.com/fachada.jpg"
                          className="w-full bg-transparent text-white text-xs font-medium outline-none placeholder-slate-600"
                        />
                      </div>
                      <button
                        onClick={handleApplyFachada}
                        disabled={!fachadaUrl}
                        className="bg-yellow-400 hover:bg-yellow-300 disabled:opacity-40 text-slate-900 font-black px-3 py-1.5 rounded-lg text-[9px] uppercase tracking-widest transition-all shrink-0 flex items-center gap-1"
                      >
                        <Check size={10} /> Aplicar
                      </button>
                    </div>
                    <p className="text-[9px] text-slate-500 mt-1 px-1 flex items-center gap-1">
                      <AlertCircle size={8} /> Salva ao clicar em "Salvar Registro no CRM".
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* ── Bloco 3: Canais de Contato (compacto) ── */}
              <div className="bg-slate-950/40 p-3 rounded-xl border border-white/5">
                <h4 className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2 flex items-center gap-1.5">
                  <User size={10} className="text-yellow-400" /> Canais de Contato
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1.5">
                  <div className="flex items-center justify-between text-xs gap-2">
                    <span className="text-slate-500 shrink-0">Telefone</span>
                    <span className="font-bold text-white text-right break-all">{phoneRaw || 'N/D'}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs gap-2">
                    <span className="text-slate-500 shrink-0">E-mail</span>
                    <span className="font-bold text-white text-right break-all">{lead.email || 'N/D'}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs gap-2">
                    <span className="text-slate-500 shrink-0">Website</span>
                    {lead.website && lead.website !== "N/D" ? (
                      <a href={lead.website} target="_blank" rel="noreferrer" className="font-bold text-yellow-400 hover:underline flex items-center gap-1 text-right break-all">
                        {lead.website} <ExternalLink size={9} className="shrink-0" />
                      </a>
                    ) : <span className="font-bold text-slate-600">N/D</span>}
                  </div>
                  <div className="flex items-center justify-between text-xs gap-2">
                    <span className="text-slate-500 shrink-0">Social</span>
                    {lead.social_url && lead.social_url !== "N/D" ? (
                      <a href={lead.social_url} target="_blank" rel="noreferrer" className="font-bold text-yellow-400 hover:underline flex items-center gap-1 text-right break-all">
                        Social <ExternalLink size={9} className="shrink-0" />
                      </a>
                    ) : <span className="font-bold text-slate-600">N/D</span>}
                  </div>
                </div>
              </div>

              {/* ── Bloco 4: Inteligência de Obra Ativa ── */}
              {lead.intencao_ativa ? (
                <div className="bg-rose-500/10 p-3 rounded-xl border border-rose-500/25 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-20 h-20 bg-rose-500/5 rounded-full blur-2xl pointer-events-none" />
                  <h4 className="text-[9px] font-black text-rose-400 uppercase tracking-[0.2em] mb-2 flex items-center gap-1.5 animate-pulse">
                    <Flame size={10} className="fill-rose-400" /> Inteligência de Obra Ativa
                  </h4>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Urgência</span>
                      <span className="font-black text-rose-400 bg-rose-500/20 px-2 py-0.5 rounded text-[10px]">
                        {lead.score_urgencia}/10
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Categoria</span>
                      <span className="font-bold text-white uppercase text-[10px] tracking-wider">
                        {lead.categoria_demanda === 'pintura_fachada' ? '🎨 Pintura' :
                         lead.categoria_demanda === 'lavagem_pastilhas' ? '🧽 Lavagem' :
                         lead.categoria_demanda === 'reforma_geral' ? '🧱 Reforma' : lead.categoria_demanda || 'N/D'}
                      </span>
                    </div>
                  </div>
                  {lead.resumo_sinal && (
                    <p className="text-xs text-white font-medium bg-slate-950/60 p-2 rounded-lg border border-white/5 leading-relaxed mt-2">
                      {lead.resumo_sinal}
                    </p>
                  )}
                </div>
              ) : null}

              {/* ── Bloco 5: Origem do Lead ── */}
              {lead.link_fonte && lead.link_fonte !== "N/D" && (
                <div className="bg-gradient-to-r from-blue-950/40 to-slate-950/60 p-3 rounded-xl border border-blue-500/20 relative overflow-hidden group shrink-0">
                  <div className="absolute top-0 right-0 w-14 h-14 bg-blue-500/5 rounded-full blur-xl pointer-events-none" />
                  <h4 className="text-[9px] font-black text-blue-400 uppercase tracking-[0.2em] mb-1.5 flex items-center gap-1.5">
                    <Globe size={10} className="text-blue-400" /> Origem do Lead
                  </h4>
                  <p className="text-[11px] text-slate-400 leading-snug mb-2">
                    Capturado via inteligência ativa da Otto.
                  </p>
                  <a
                    href={lead.link_fonte}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 hover:border-blue-500/50 text-blue-300 font-bold px-3 py-1.5 rounded-lg text-[10px] transition-all group-hover:scale-[1.01]"
                  >
                    Acessar Canal de Origem <ExternalLink size={10} />
                  </a>
                </div>
              )}
            </div>

            {/* ── Coluna 2: CRM ── */}
            <div className={`flex-1 flex flex-col gap-4 sm:gap-5 justify-between md:overflow-y-auto md:max-h-full pr-2 scrollbar-thin ${readOnly ? "pt-10 md:pt-6" : "pt-8 md:pt-0"}`}>
              <div className="space-y-4 sm:space-y-5">
                <div>
                  <h3 className="text-base sm:text-lg font-black text-white uppercase tracking-tight mb-1">CRM Otto Pinturas</h3>
                  <p className="text-xs text-slate-400 font-medium">Registre o andamento do contato e converse com o administrador.</p>
                </div>

                {/* Status da Abordagem */}
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                    <Star size={11} className="text-yellow-400" /> Status da Abordagem
                  </label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    disabled={readOnly}
                    className="w-full bg-slate-950 border border-white/10 rounded-2xl p-3.5 text-sm font-bold text-white focus:outline-none focus:border-yellow-400 appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <option value="Aguardando Abordagem">🟡 Aguardando Abordagem</option>
                    <option value="Contato Iniciado">🔵 Contato Iniciado (WhatsApp/Ligação)</option>
                    <option value="Proposta Enviada">📧 Proposta Comercial Enviada</option>
                    <option value="Reunião Agendada">📅 Reunião Agendada</option>
                    <option value="Negócio Fechado">✅ Negócio Fechado (Pintura Otto)</option>
                    <option value="Sem Interesse">❌ Sem Interesse / Sem Demanda</option>
                  </select>
                </div>

                {/* Bloco de Notas Pessoais */}
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                    <ScrollText size={11} className="text-yellow-400" /> Bloco de Notas
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    disabled={readOnly}
                    placeholder={readOnly ? "Sem notas." : "Anotações pessoais sobre este lead..."}
                    rows={3}
                    className="w-full bg-slate-950 border border-white/10 focus:border-yellow-400 rounded-2xl p-4 text-sm text-white outline-none placeholder-slate-600 transition-colors resize-none font-medium leading-relaxed disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Bate-Papo do Lead */}
                <div className="bg-slate-900/50 border border-white/5 rounded-2xl overflow-hidden min-h-[280px] lg:min-h-[350px]">
                  <ChatPanel
                    leadId={leadId}
                    currentUser={currentUser || { id: 0, name: "", role: "" }}
                    isReadOnly={false}
                  />
                </div>

                {/* Agendamento de Retorno */}
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                    <Clock size={11} className="text-yellow-400" /> Agendar retorno
                  </label>
                  <input
                    type="datetime-local"
                    value={returnDate}
                    onChange={(e) => setReturnDate(e.target.value)}
                    disabled={readOnly}
                    className="w-full bg-slate-950 border border-white/10 focus:border-yellow-400 rounded-2xl p-3.5 text-xs font-bold text-white outline-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>

               {/* Botão Salvar */}
               <button
                 onClick={handleSave}
                 disabled={saving}
                 className="w-full bg-yellow-400 hover:bg-yellow-300 disabled:bg-slate-800 disabled:text-slate-600 text-slate-900 font-black py-4 rounded-2xl flex items-center justify-center gap-2 transition-all transform active:scale-[0.98] shadow-lg shadow-yellow-400/10 mt-auto"
               >
                 {saving ? (
                   <>
                     <Loader2 className="animate-spin" size={16} />
                     <span className="uppercase tracking-widest text-xs">Salvando...</span>
                   </>
                 ) : (
                   <>
                     <Save size={16} />
                     <span className="uppercase tracking-widest text-xs">Salvar Registro no CRM</span>
                 </>
               )}
             </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  if (!mounted) return null;

  return createPortal(modalContent, document.body);
}
