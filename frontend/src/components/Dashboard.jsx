import { useEffect, useState } from "react";

const API_BASE = "/api";

export default function Dashboard({ user, onLogout }) {

  const [tricounts, setTricounts] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedTricount, setSelectedTricount] = useState(null);

  const [loadingList, setLoadingList] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");

  const [newName, setNewName] = useState("");

  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");

  const [desc, setDesc] = useState("");
  const [amount, setAmount] = useState("");
  const [payerId, setPayerId] = useState("");
  const [participants, setParticipants] = useState([]);

  const [splitMode, setSplitMode] = useState("equal");
  const [weights, setWeights] = useState({});
  const [expandedExpenseId, setExpandedExpenseId] = useState(null);

  useEffect(() => {
    loadTricounts();
  }, []);

  async function loadTricounts() {
    try {
      setLoadingList(true);
      setError("");
      const res = await fetch(`${API_BASE}/tricounts`);
      if (!res.ok) {
        throw new Error("Failed to load tricounts");
      }
      const data = await res.json();
      setTricounts(data);
    } catch (e) {
      console.error(e);
      setError("Erreur lors du chargement des tricounts.");
    } finally {
      setLoadingList(false);
    }
  }

  async function loadTricountDetail(id) {
    try {
      setLoadingDetail(true);
      setError("");
      const res = await fetch(`${API_BASE}/tricounts/${id}`);
      if (!res.ok) {
        if (res.status === 404) {
          setSelectedTricount(null);
          setError("Tricount introuvable (404).");
          return;
        }
        throw new Error("Failed to load tricount detail");
      }
      const data = await res.json();
      setSelectedTricount(data);
      setSelectedId(id);

      setUserName("");
      setUserEmail("");
      setDesc("");
      setAmount("");
      setPayerId("");
      setParticipants([]);
    } catch (e) {
      console.error(e);
      setError("Erreur lors du chargement du tricount.");
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleCreateTricount(e) {
    e.preventDefault();
    if (!newName.trim()) return;

    try {
      setError("");
      const res = await fetch(`${API_BASE}/tricounts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName.trim() }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Erreur création tricount.");
      }

      const created = await res.json();
      setNewName("");
      await loadTricounts();
      await loadTricountDetail(created.id);
    } catch (e) {
      console.error(e);
      setError(e.message || "Erreur lors de la création du tricount.");
    }
  }

  async function handleAddUser(e) {
    e.preventDefault();
    if (!selectedTricount) return;
    if (!userName.trim()) return;

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedTricount.id}/users`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: userName.trim(),
            email: userEmail.trim() || null,
          }),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Erreur ajout utilisateur.");
      }

      await loadTricountDetail(selectedTricount.id);
      await loadTricounts();
    } catch (e) {
      console.error(e);
      setError(e.message || "Erreur réseau lors de l'ajout utilisateur.");
    }
  }

  function toggleParticipant(id) {
    setParticipants((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleAddExpense(e) {
      e.preventDefault();
      if (!selectedTricount) return;

      if (!desc.trim() || !amount || !payerId || participants.length === 0) {
        setError("Merci de remplir tous les champs (et au moins un participant).");
        return;
      }

      const payload = {
        description: desc.trim(),
        amount: parseFloat(amount),
        payer_id: payerId,
        participants_ids: participants,
        weights: {},
      };

      if (splitMode === "weighted") {
        const weightMap = {};
        participants.forEach((uid) => {
          weightMap[uid] = parseFloat(weights[uid]) || 0;
        });
        payload.weights = weightMap;
      }

      try {
        setError("");
        const res = await fetch(
          `${API_BASE}/tricounts/${selectedTricount.id}/expenses`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.error || "Erreur ajout dépense.");
        }

        await loadTricountDetail(selectedTricount.id);
        await loadTricounts();

        setDesc(""); setAmount("");
      } catch (e) {
        console.error(e);
        setError(e.message || "Erreur réseau lors de l'ajout dépense.");
      }
    }

  async function handleDeleteUser(userId) {
    if (!selectedId) return;
    if (!window.confirm("Supprimer cet utilisateur ?")) return;

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedId}/users/${userId}`,
        { method: "DELETE" }
      );
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Erreur lors de la suppression.");
        return;
      }

      setSelectedTricount(data);
      loadTricounts();
    } catch (e) {
      console.error(e);
      setError("Erreur réseau suppression utilisateur.");
    }
  }

  async function handleDeleteExpense(expenseId) {
    if (!selectedId) return;
    if (!window.confirm("Supprimer cette dépense ?")) return;

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedId}/expenses/${expenseId}`,
        { method: "DELETE" }
      );
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Erreur suppression dépense.");
        return;
      }
      setSelectedTricount(data);
      loadTricounts();
    } catch (e) {
      console.error(e);
      setError("Erreur réseau suppression dépense.");
    }
  }

  async function handleExportExcel() {
    if (!selectedTricount) return;

    try {
      const res = await fetch(
        `/api/tricounts/${selectedTricount.id}/export/excel`
      );

      if (!res.ok) {
        throw new Error("Export failed");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedTricount.name || "tricount"}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      setError("Erreur lors de l'export Excel.");
    }
  }
  async function handleDeleteTricount() {
    if (!selectedTricount) return;

    const confirmed = window.confirm(
      "Êtes-vous sûr de vouloir supprimer ce tricount ? Cette action est définitive."
    );
    if (!confirmed) return;

    try {
      setError("");

      const res = await fetch(
        `/api/tricounts/${selectedTricount.id}`,
        { method: "DELETE" }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Erreur lors de la suppression du tricount.");
      }


      setSelectedTricount(null);
      setSelectedId(null);

      await loadTricounts();
    } catch (e) {
      console.error(e);
      setError(e.message || "Erreur réseau lors de la suppression.");
    }
  }


  const balances = selectedTricount?.balances || {};
  const settlements = selectedTricount?.settlements || [];


  return (
    <div className="max-w-6xl mx-auto flex gap-6 px-6 py-8">
      <aside className="w-1/3 bg-white border border-slate-200 rounded-2xl p-4 flex flex-col gap-4 dark:bg-slate-900 dark:border-slate-800">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">3Comptes</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
               {user?.name ? `Bonjour, ${user.name}` : "Gestion de dépenses"}
            </p>
          </div>


          <button
             onClick={onLogout}
             className="text-xs text-red-500 hover:text-red-600 hover:underline px-2"
          >
             Déconnexion
          </button>
        </header>

        {loadingList && (
          <p className="text-xs text-slate-500">Chargement...</p>
        )}
        {error && (
          <div className="text-xs text-red-800 bg-red-100 p-2 rounded border border-red-200">
            {error}
          </div>
        )}

        <div className="flex-1 flex flex-col gap-2 overflow-hidden">
          <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            Mes tricounts
          </h2>
          <div className="flex-1 overflow-y-auto pr-1">
            {tricounts.length === 0 ? (
              <p className="text-xs text-slate-500">Aucun tricount.</p>
            ) : (
              <ul className="space-y-1 text-sm">
                {tricounts.map((t) => (
                  <li key={t.id}>
                    <button
                      onClick={() => loadTricountDetail(t.id)}
                      className={`w-full text-left px-3 py-2 rounded-xl border text-xs transition
                        ${
                          t.id === selectedId
                            ? "border-emerald-500/70 bg-emerald-500/10 text-emerald-900 dark:text-emerald-100"
                            : "border-transparent bg-slate-100 hover:bg-slate-50 dark:bg-slate-800/60"
                        }`}
                    >
                      <div className="flex justify-between">
                        <span className="font-semibold">{t.name}</span>
                        <span className="text-[10px] text-slate-400">{t.currency}</span>
                      </div>
                      <div className="text-[10px] text-slate-500">
                        {t.users_count} Utilisateurs • {t.expenses_count} Dépenses
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="border-t border-slate-200 pt-3 dark:border-slate-800">
          <h3 className="text-xs font-semibold mb-2 text-slate-700 dark:text-slate-300">Nouveau tricount</h3>
          <form onSubmit={handleCreateTricount} className="space-y-2">
            <input
              type="text"
              placeholder="Ex : Voyage..."
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs outline-none focus:ring-1 focus:ring-emerald-500 dark:bg-slate-900 dark:border-slate-700"
            />
            <button
              type="submit"
              className="w-full rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-400 transition"
            >
              Créer
            </button>
          </form>
        </div>
      </aside>

      <main className="flex-1 flex flex-col gap-4">
        {!selectedTricount && !loadingDetail && (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            Sélectionne un tricount à gauche.
          </div>
        )}
        {loadingDetail && <div className="text-center text-slate-400 text-sm">Chargement...</div>}

        {selectedTricount && (
          <>
            <section className="bg-white border border-slate-200 rounded-2xl p-4 flex justify-between dark:bg-slate-900 dark:border-slate-800">
              <div>
                 <h2 className="text-lg font-semibold">{selectedTricount.name}</h2>
                 <p className="text-xs text-slate-500">Devise : {selectedTricount.currency}</p>
              </div>
              <div className="flex gap-2">

                <button
                  onClick={handleExportExcel}
                  className="text-xs bg-emerald-500 text-white px-3 py-1 rounded hover:bg-emerald-600"
                >
                  Exporter Excel
                </button>
                <button
                  onClick={handleDeleteTricount}
                  className="text-xs bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                >
                  Supprimer
                </button>
              </div>
            </section>

            <div className="grid grid-cols-2 gap-4">

               <section className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col gap-3 dark:bg-slate-900 dark:border-slate-800">
                  <div className="flex justify-between">
                     <h3 className="text-sm font-semibold">Utilisateurs</h3>
                     <span className="text-[10px] text-slate-400">{selectedTricount.users.length}</span>
                  </div>
                  <div className="space-y-2 max-h-52 overflow-y-auto">
                     {selectedTricount.users.map(u => (
                        <div key={u.id} className="flex justify-between items-center text-xs bg-slate-50 p-2 rounded dark:bg-slate-800/70">
                           <div>
                              <div className="font-medium">{u.name}</div>
                              <div className="text-[10px] text-slate-400">{u.email}</div>
                           </div>
                           <button onClick={() => handleDeleteUser(u.id)} className="text-red-400 hover:text-red-600">×</button>
                        </div>
                     ))}
                  </div>
                  <form onSubmit={handleAddUser} className="space-y-2 border-t pt-2 border-slate-100 dark:border-slate-700">
                     <input type="text" placeholder="Nom" value={userName} onChange={e => setUserName(e.target.value)} className="w-full rounded border border-slate-300 px-2 py-1 text-xs dark:bg-slate-950 dark:border-slate-700" />
                     <input type="email" placeholder="Email (opt)" value={userEmail} onChange={e => setUserEmail(e.target.value)} className="w-full rounded border border-slate-300 px-2 py-1 text-xs dark:bg-slate-950 dark:border-slate-700" />
                     <button type="submit" className="w-full bg-slate-800 text-white text-xs py-1 rounded">Ajouter</button>
                  </form>
               </section>

               <section className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col gap-3 dark:bg-slate-900 dark:border-slate-800">
                  <div className="flex justify-between">
                     <h3 className="text-sm font-semibold">Dépenses</h3>
                     <span className="text-[10px] text-slate-400">{selectedTricount.expenses.length}</span>
                  </div>

                  <div className="space-y-2 max-h-52 overflow-y-auto">
                    {selectedTricount.expenses.map((e) => {
                      const payer = selectedTricount.users.find((u) => u.id === e.payer_id);
                      const isExpanded = expandedExpenseId === e.id;

                      return (
                        <div
                          key={e.id}
                          className={`p-2 rounded text-xs flex flex-col transition-colors cursor-pointer ${
                            isExpanded
                              ? "bg-emerald-50 border border-emerald-100 dark:bg-emerald-900/20"
                              : "bg-slate-50 hover:bg-slate-100 dark:bg-slate-800/70"
                          }`}
                          onClick={() => setExpandedExpenseId(isExpanded ? null : e.id)}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium text-slate-800 dark:text-slate-200">
                                {e.description}
                              </div>
                              <div className="text-[10px] text-slate-500">
                                {Number(e.amount).toFixed(2)} {e.currency} • Payé par{" "}
                                <span className="font-semibold">{payer?.name || "?"}</span>
                              </div>
                            </div>
                            <button
                              onClick={(ev) => {
                                ev.stopPropagation();
                                handleDeleteExpense(e.id);
                              }}
                              className="text-slate-400 hover:text-red-500 px-2"
                            >
                              ×
                            </button>
                          </div>

                          {isExpanded && (
                            <div className="mt-2 pt-2 border-t border-slate-200/50 dark:border-slate-700">
                              <span className="block mb-1 font-semibold text-[10px] text-slate-600 dark:text-slate-400">
                                Concernant :
                              </span>
                              <div className="flex flex-wrap gap-1">
                                {e.participants_ids.map((pid) => {
                                  const pName = selectedTricount.users.find((u) => u.id === pid)?.name;
                                  const weight = e.weights && e.weights[pid];

                                  return (
                                    <span
                                      key={pid}
                                      className="bg-white border border-slate-200 px-1.5 py-0.5 rounded text-[10px] text-slate-600 dark:bg-slate-900 dark:border-slate-700 dark:text-slate-300"
                                    >
                                      {pName}
                                      {weight ? (
                                        <span className="ml-1 text-emerald-500 font-mono">
                                          (x{weight})
                                        </span>
                                      ) : null}
                                    </span>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <form onSubmit={handleAddExpense} className="space-y-2 border-t pt-2 border-slate-100 dark:border-slate-700 text-xs">
                     <input type="text" placeholder="Quoi ?" value={desc} onChange={e => setDesc(e.target.value)} className="w-full rounded border px-2 py-1 dark:bg-slate-950 dark:border-slate-700" />
                     <input type="number" placeholder="Combien ?" value={amount} onChange={e => setAmount(e.target.value)} className="w-full rounded border px-2 py-1 dark:bg-slate-950 dark:border-slate-700" />

                     <div className="flex items-center gap-2">
                        <span>Payeur:</span>
                        <select value={payerId} onChange={e => setPayerId(e.target.value)} className="flex-1 border rounded py-1 dark:bg-slate-950 dark:border-slate-700">
                           <option value="">--</option>
                           {selectedTricount.users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                        </select>
                     </div>
                     <div className="mt-2">
                      <div className="flex justify-between items-end mb-1">
                        <span className="block mb-1 font-semibold">Pour qui :</span>
                        <button
                          type="button"
                          onClick={() => {
                            if (participants.length === selectedTricount.users.length) {
                              setParticipants([]);
                            } else {
                              setParticipants(selectedTricount.users.map((u) => u.id));
                            }
                          }}
                          className="text-[10px] text-emerald-500 hover:underline mb-1"
                        >
                          {participants.length === selectedTricount.users.length
                            ? "Aucun"
                            : "Tous"}
                        </button>
                      </div>

                      <div className="flex gap-4 mb-2 text-xs">
                        <label className="flex items-center gap-1 cursor-pointer">
                          <input
                            type="radio"
                            name="mode"
                            checked={splitMode === "equal"}
                            onChange={() => setSplitMode("equal")}
                          />
                          Équitable
                        </label>
                        <label className="flex items-center gap-1 cursor-pointer">
                          <input
                            type="radio"
                            name="mode"
                            checked={splitMode === "weighted"}
                            onChange={() => setSplitMode("weighted")}
                          />
                          Pondéré
                        </label>
                      </div>

                      <div className="flex flex-col gap-1 max-h-40 overflow-y-auto border border-slate-100 p-1 rounded dark:border-slate-800">
                        {selectedTricount.users.map((u) => (
                          <div
                            key={u.id}
                            className="flex items-center justify-between bg-slate-50 p-1.5 rounded dark:bg-slate-800"
                          >
                            <label className="flex items-center gap-2 cursor-pointer text-xs flex-1">
                              <input
                                type="checkbox"
                                checked={participants.includes(u.id)}
                                onChange={() => toggleParticipant(u.id)}
                              />
                              {u.name}
                            </label>

                            {splitMode === "weighted" && participants.includes(u.id) && (
                              <div className="flex items-center gap-1">
                                <input
                                  type="number"
                                  placeholder="1"
                                  className="w-12 text-right text-xs border rounded p-1 outline-none focus:border-emerald-500 dark:bg-slate-900 dark:border-slate-700"
                                  value={weights[u.id] || ""}
                                  onChange={(e) =>
                                    setWeights({ ...weights, [u.id]: e.target.value })
                                  }
                                />
                                <span className="text-[10px] text-slate-400">pd</span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                     <button type="submit" className="w-full bg-emerald-500 text-white py-1 rounded">Ajouter dépense</button>
                  </form>
               </section>
            </div>

            <div className="grid grid-cols-2 gap-4">
               <section className="bg-white border border-slate-200 rounded-2xl p-4 dark:bg-slate-900 dark:border-slate-800">
                  <h3 className="text-sm font-semibold mb-2">Soldes</h3>
                  <ul className="space-y-1 text-xs">
                     {selectedTricount.users.map(u => {
                        const bal = balances[u.id] || 0;
                        const color = bal > 0 ? "text-green-600" : bal < 0 ? "text-red-600" : "text-slate-500";
                        return (
                           <li key={u.id} className="flex justify-between bg-slate-50 p-2 rounded dark:bg-slate-800/70">
                              <span>{u.name}</span>
                              <span className={color}>{bal.toFixed(2)}</span>
                           </li>
                        )
                     })}
                  </ul>
               </section>
               <section className="bg-white border border-slate-200 rounded-2xl p-4 dark:bg-slate-900 dark:border-slate-800">
                  <h3 className="text-sm font-semibold mb-2">Règlements</h3>
                  <ul className="space-y-1 text-xs">
                     {settlements.map((s, idx) => {
                        const u1 = selectedTricount.users.find(u => u.id === (s.from_id || s.from));
                        const u2 = selectedTricount.users.find(u => u.id === (s.to_id || s.to));
                        return (
                           <li key={idx} className="flex justify-between bg-slate-50 p-2 rounded dark:bg-slate-800/70">
                              <span>{u1?.name} → {u2?.name}</span>
                              <span className="font-mono">{Number(s.amount).toFixed(2)}</span>
                           </li>
                        )
                     })}
                  </ul>
               </section>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
