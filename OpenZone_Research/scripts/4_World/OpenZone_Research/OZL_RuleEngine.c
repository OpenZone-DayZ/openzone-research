// Правила переробки на живих предметах: підбір правила по карго приладу,
// план входу й витратних матеріалів, чистота й бали циклу, розігрування
// виходів.
//
// Контракт атомарності: СПОЧАТКУ весь план (вхід + витратні) без змін, ПОТІМ
// усі списання. Бали прилад не нараховує -- він виробляє носій, бали дає
// термінал. InputItem.ConsumeInput лишився в конфігу й тут не читається: вхід
// фонової станції списується завжди, це і є антифарм.

class OZL_RuleEngine
{
    static bool MatchInput(string actualType, string cfgClass)
    {
        return OZL_Match.MatchClass(actualType, cfgClass);
    }

    // Правило для ручного запуску: гравець є, власник -- його, RequiredWorn
    // перевіряється на ньому.
    static OZL_Rule FindStartable(EntityAI device, PlayerBase player, string owner, out string why)
    {
        return FindCore(device, player, owner, null, why);
    }

    // Правило для автопродовження: гравця немає, власник заморожений при
    // старті, RequiredWorn пропускається (нема на кому перевіряти). Класи,
    // щойно вироблені цим приладом, виключаються -- інакше правило, чий вхід
    // збігається з чиїмось виходом на тому ж приладі, з'їло б власний
    // результат за секунду після виробництва.
    static OZL_Rule FindAutoContinue(EntityAI device, string owner, array<string> exclClasses, out string why)
    {
        return FindCore(device, null, owner, exclClasses, why);
    }

    // Питання те саме, що ставить план карго: «чи взяло б це правило те, що
    // ми щойно виробили?» -- тому й запитуємо тією самою функцією.
    private static bool IsExcluded(OZL_Rule r, array<string> exclClasses)
    {
        if (!exclClasses)
            return false;
        for (int i = 0; i < exclClasses.Count(); i++)
        {
            if (MatchInput(exclClasses[i], r.InputItem.Classname))
                return true;
        }
        return false;
    }

    // Перше правило цього приладу в порядку конфігу, дозволене власникові,
    // чий повний план збирається по карго. Порядок у файлі -- пріоритет
    // адміна. Причина відмови -- ключ рядка, подробиці -- в лог рівня dbg:
    // гравцеві не треба знати id чужих правил. Причина правила, чий вхід у
    // карго є (вузол, одяг, інструмент), важливіша за «немає входу» решти:
    // інакше кляп замість ганчірки показував «бракує інструмента» від
    // сусіднього правила з бинтом (стенд, 2026-10-30).
    private static OZL_Rule FindCore(EntityAI device, PlayerBase player, string owner, array<string> exclClasses, out string why)
    {
        why = "STR_OZL_ERR_NO_RULE";
        bool inputSeen = false;
        OZL_FactionState st = OZL_State.Get(owner);
        OZL_Rules rules = OZL_Config.Get().Rules();
        string type = device.GetType();

        for (int g = 0; g < rules.Groups.Count(); g++)
        {
            OZL_RuleGroup grp = rules.Groups[g];
            if (!grp)
                continue;
            for (int i = 0; i < grp.Rules.Count(); i++)
            {
                OZL_Rule r = grp.Rules[i];
                if (!r || !r.Enabled)
                    continue;
                if (!OZL_Match.MatchClass(type, r.Device))
                    continue;
                if (IsExcluded(r, exclClasses))
                    continue;
                // Фракційний відсів -- першим і мовчки: чуже правило для
                // цього власника не існує.
                if (r.RequiredFactions.Count() > 0 && r.RequiredFactions.Find(owner) < 0)
                    continue;

                array<ItemBase> planItems   = new array<ItemBase>();
                array<int>      planAmounts = new array<int>();
                array<int>      planInputs  = new array<int>();
                string planWhy;
                if (!BuildCargoPlan(device, r, planItems, planAmounts, planInputs, planWhy))
                {
                    if (!inputSeen)
                        why = "STR_OZL_ERR_NEED_INPUT";
                    OZL_Log.Dbg("rule '" + r.Id + "' on " + type + ": " + planWhy);
                    continue;
                }

                if (r.RequiredNode != "")
                {
                    bool done = false;
                    if (st)
                        done = st.IsCompleted(r.RequiredNode);
                    if (!done)
                    {
                        why = "STR_OZL_ERR_NEED_NODE";
                        inputSeen = true;
                        OZL_Log.Dbg("rule '" + r.Id + "' on " + type + ": owner '" + owner + "' lacks node '" + r.RequiredNode + "'");
                        continue;
                    }
                }

                string missing;
                if (player && !OZL_Gear.WearsAll(player, r.RequiredWorn, missing))
                {
                    why = "STR_OZL_ERR_NEED_WORN";
                    inputSeen = true;
                    OZL_Log.Dbg("rule '" + r.Id + "' on " + type + ": player wears no '" + missing + "'");
                    continue;
                }
                if (!OZL_Gear.DeviceHasTools(device, r.RequiredTools, missing))
                {
                    why = "STR_OZL_ERR_NEED_TOOL";
                    inputSeen = true;
                    OZL_Log.Dbg("rule '" + r.Id + "' on " + type + ": device has no tool '" + missing + "'");
                    continue;
                }
                return r;
            }
        }
        return null;
    }

    // ---------- план карго ----------

    // Скільки одиниць цього предмета вже заплановано.
    private static int PlannedFor(ItemBase ib, array<ItemBase> planItems, array<int> planAmounts)
    {
        int idx = planItems.Find(ib);
        if (idx > -1)
            return planAmounts[idx];
        return 0;
    }

    // Кандидат вкладений в уже запланований предмет або є його предком --
    // виключаємо: залишок стака всередині видаленого батька гине разом із
    // ним (карго вмирає з контейнером наприкінці кадру) = прихована
    // переплата гравця.
    private static bool IsNestedConflict(ItemBase ib, array<ItemBase> planItems)
    {
        EntityAI par = ib.GetHierarchyParent();
        while (par)
        {
            ItemBase parIb = ItemBase.Cast(par);
            if (parIb && planItems.Find(parIb) > -1)
                return true;
            par = par.GetHierarchyParent();
        }
        for (int i = 0; i < planItems.Count(); i++)
        {
            if (IsAncestorOf(ib, planItems[i]))
                return true;
        }
        return false;
    }

    private static bool IsAncestorOf(ItemBase candidate, ItemBase child)
    {
        EntityAI par = child.GetHierarchyParent();
        while (par)
        {
            if (par == candidate)
                return true;
            par = par.GetHierarchyParent();
        }
        return false;
    }

    // Доступна кількість: стак -- quantity, інакше одиниця.
    private static int AvailOf(ItemBase ib)
    {
        if (ib.ConfigGetBool("canBeSplit"))
            return ib.GetQuantity();
        return 1;
    }

    // «Повний» предмет для RequireFullQuantity: заряд або стак на максимумі.
    // Нуль максимуму -- «квантитету немає взагалі», вимога не діє. Допуск на
    // тисячні: quantity -- float, і повний заряд після збереження буває на
    // крихту менший за максимум.
    private static bool IsFullQuantity(ItemBase ib)
    {
        int qmax = ib.GetQuantityMax();
        if (qmax <= 0)
            return true;
        return ib.GetQuantity() >= qmax - 0.001;
    }

    // Предмет стоїть у слоті вкладення приладу (інструмент, модуль), а не
    // лежить у карго: EnumerateInventory обходить і те, і те.
    private static bool IsDeviceAttachment(EntityAI device, EntityAI candidate)
    {
        if (!device || !candidate || !device.GetInventory())
            return false;
        int n = device.GetInventory().AttachmentCount();
        for (int i = 0; i < n; i++)
        {
            if (device.GetInventory().GetAttachmentFromIndex(i) == candidate)
                return true;
        }
        return false;
    }

    // Чи придатний предмет карго як сировина або витратний матеріал.
    private static bool Usable(EntityAI device, ItemBase ib)
    {
        if (!ib || ib == device)
            return false;
        if (IsDeviceAttachment(device, ib))
            return false;
        // Зруйноване не береться: мовчки з'їло б цикл.
        if (ib.IsRuined())
            return false;
        return true;
    }

    // Єдиний план (вхід + витратні матеріали) по карго приладу, без списань.
    // inputAmounts -- паралельний масив: скільки з кожного запису належить
    // ВХОДУ. Без нього пробу аналізу не відрізнити від витратника того ж
    // класу. Один предмет може служити обом ролям, тож плани не розділити.
    static bool BuildCargoPlan(EntityAI device, OZL_Rule rule, array<ItemBase> planItems, array<int> planAmounts, array<int> inputAmounts, out string why)
    {
        why = "";
        array<EntityAI> cargo = new array<EntityAI>();
        device.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, cargo);

        int inRemaining = rule.InputItem.Quantity;
        for (int c = 0; c < cargo.Count(); c++)
        {
            if (inRemaining <= 0)
                break;
            ItemBase ib = ItemBase.Cast(cargo[c]);
            if (!Usable(device, ib))
                continue;
            if (!MatchInput(ib.GetType(), rule.InputItem.Classname))
                continue;
            // Проба без чинного рядка -- порожня: аналізатор її не бере.
            if (OZL_Lines.IsSample(ib.GetType()) && !OZL_Sample_Base.HasPayload(ib))
                continue;
            if (rule.InputItem.RequireFullQuantity && !IsFullQuantity(ib))
                continue;
            if (IsNestedConflict(ib, planItems))
                continue;
            int avail = AvailOf(ib) - PlannedFor(ib, planItems, planAmounts);
            if (avail <= 0)
                continue;
            int take = avail;
            if (take > inRemaining)
                take = inRemaining;
            int idx = planItems.Find(ib);
            if (idx > -1)
            {
                planAmounts[idx]  = planAmounts[idx] + take;
                inputAmounts[idx] = inputAmounts[idx] + take;
            }
            else
            {
                planItems.Insert(ib);
                planAmounts.Insert(take);
                inputAmounts.Insert(take);
            }
            inRemaining -= take;
        }
        if (inRemaining > 0)
        {
            why = "needs " + rule.InputItem.Quantity.ToString() + " x " + rule.InputItem.Classname + " in cargo";
            if (rule.InputItem.RequireFullQuantity)
                why += " (full stacks or charges only)";
            return false;
        }

        for (int k = 0; k < rule.Consumables.Count(); k++)
        {
            OZL_RuleConsumable con = rule.Consumables[k];
            if (!con)
                continue;
            int remaining = con.Quantity;
            for (int c2 = 0; c2 < cargo.Count(); c2++)
            {
                if (remaining <= 0)
                    break;
                ItemBase ib2 = ItemBase.Cast(cargo[c2]);
                if (!Usable(device, ib2))
                    continue;
                if (!MatchInput(ib2.GetType(), con.Classname))
                    continue;
                if (IsNestedConflict(ib2, planItems))
                    continue;
                int avail2 = AvailOf(ib2) - PlannedFor(ib2, planItems, planAmounts);
                if (avail2 <= 0)
                    continue;
                int take2 = avail2;
                if (take2 > remaining)
                    take2 = remaining;
                int idx2 = planItems.Find(ib2);
                if (idx2 > -1)
                {
                    // inputAmounts не росте: це витратний матеріал
                    planAmounts[idx2] = planAmounts[idx2] + take2;
                }
                else
                {
                    planItems.Insert(ib2);
                    planAmounts.Insert(take2);
                    inputAmounts.Insert(0);
                }
                remaining -= take2;
            }
            if (remaining > 0)
            {
                why = "short of " + remaining.ToString() + " x " + con.Classname + " in cargo";
                return false;
            }
        }
        return true;
    }

    static void ConsumePlan(array<ItemBase> planItems, array<int> planAmounts)
    {
        for (int i = 0; i < planItems.Count(); i++)
        {
            ItemBase ib = planItems[i];
            if (!ib)
                continue;
            int amt = planAmounts[i];
            if (ib.ConfigGetBool("canBeSplit") && ib.GetQuantity() > amt)
                ib.AddQuantity(-amt);
            else
                GetGame().ObjectDelete(ib);
        }
    }

    // ---------- чистота й бали ----------
    //
    // Пакувальник: чистота проби -- Purity правила плюс модулі лінії (OZL_Gear),
    // бали -- Points виходу. Аналізатор: чистота проби -- шанс, її бали
    // переходять у носій. Знімок -- при старті, поки з'їдені предмети ще існують.

    static bool PlanSample(array<ItemBase> planItems, array<int> inputAmounts, out int points, out int purityPct)
    {
        points = 0;
        purityPct = 0;
        for (int i = 0; i < planItems.Count(); i++)
        {
            if (i >= inputAmounts.Count() || inputAmounts[i] < 1)
                continue;
            OZL_Sample_Base smp = OZL_Sample_Base.Cast(planItems[i]);
            if (smp && smp.OZL_Read(points, purityPct))
                return true;
        }
        return false;
    }

    // Розігрування виходів наприкінці циклу -- рівно один раз; подвійний вихід --
    // ще один кидок після них.
    static void ResolveResult(OZL_Rule rule, float chanceMul, float doubleChance, int carrierPoints, int purityPct, array<string> outItems, array<string> outPayloads)
    {
        for (int o = 0; o < rule.Outputs.Count(); o++)
        {
            OZL_RuleOutput def = rule.Outputs[o];
            if (!def)
                continue;
            float chance = def.Chance * chanceMul;
            if (chance > 1.0)
                chance = 1.0;
            if (Math.RandomFloat01() > chance)
                continue;
            string payload = PayloadFor(def, carrierPoints, purityPct);
            for (int i = 0; i < def.Quantity; i++)
            {
                outItems.Insert(def.Classname);
                outPayloads.Insert(payload);
            }
        }
        if (outItems.Count() == 0 || doubleChance <= 0)
            return;
        if (Math.RandomFloat01() >= doubleChance)
            return;
        int n = outItems.Count();
        for (int d = 0; d < n; d++)
        {
            outItems.Insert(outItems[d]);
            outPayloads.Insert(outPayloads[d]);
        }
    }

    static string PayloadFor(OZL_RuleOutput def, int carrierPoints, int purityPct)
    {
        if (OZL_Lines.IsSample(def.Classname))
            return OZL_Payload.EncodeSample(def.Points, purityPct);
        if (OZL_Lines.IsCarrier(def.Classname))
            return OZL_Payload.EncodeCarrier(carrierPoints);
        return "";
    }

    // Один предмет у карго приладу. На підлогу не скидаємо: те, чому не
    // знайшлося місця, лишається записом у станції й матеріалізується, коли
    // є куди. Повертає сутність.
    static EntityAI SpawnOneToCargo(EntityAI device, string classname, string payload)
    {
        EntityAI created = device.GetInventory().CreateInInventory(classname);
        if (!created)
            return null;
        OZL_Sample_Base smp = OZL_Sample_Base.Cast(created);
        if (smp)
            smp.OZL_SetPayload(payload);
        OZL_Carrier_Base car = OZL_Carrier_Base.Cast(created);
        if (car)
            car.OZL_SetPayload(payload);
        return created;
    }
}
