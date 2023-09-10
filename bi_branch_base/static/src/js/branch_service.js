/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { symmetricalDifference } from "@web/core/utils/arrays";
import { session } from "@web/session";
var ajax = require('web.ajax');

function parseBranchIds(bidsFromHash) {
    const bids = [];
    if (typeof bidsFromHash === "string") {
        bids.push(...bidsFromHash.split(",").map(Number));
    } else if (typeof bidsFromHash === "number") {
        bids.push(bidsFromHash);
    }
    return bids;
}

function computeAllowedBranchIds(bids) {
    const { user_branches } = session;
    let allowedBranchIds = bids || [];
    const availableBranchesFromSession = user_branches.allowed_branches;
    const notReallyAllowedBranches = allowedBranchIds.filter(
        (id) => !(id in availableBranchesFromSession)
    );

    if (!allowedBranchIds.length || notReallyAllowedBranches.length) {
        allowedBranchIds = [user_branches.current_branch];
    }
    return allowedBranchIds;
}

export const branchService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {
        let bids;
        let list = [];
        let dict = {};
        if ("bids" in router.current.hash) {
            bids = parseBranchIds(router.current.hash.bids);
        } else if ("bids" in cookie.current) {
            bids = parseBranchIds(cookie.current.bids);
        }
        const allowedBranchIds = computeAllowedBranchIds(bids);

        const stringCIds = allowedBranchIds.join(",");
        router.replaceState({ bids: stringCIds }, { lock: true });
        cookie.setCookie("bids", stringCIds);
        user.updateContext({ allowed_branch_ids: allowedBranchIds });
        const availablecompany = env.services.company.allowedCompanyIds;
        // console.log('------------------> availablecompany ', availablecompany);
        let availableBranches = session.user_branches.allowed_branches;
        // console.log('------------------> availableBranches ', availableBranches);

        for (const [key, value] of Object.entries(availableBranches)) {
            // console.log('------------------> key, value ', key, value);
            for (const [key1, value1] of Object.entries(availablecompany)) {
                // console.log('------------------> key1, value1 ', key1, value1);
                if(value['company'] === value1){
                    dict[key] = value
                }
            }
        }
        // console.log('------------------> dict ', dict);
        list.push(dict)
        // console.log('------------------> list ', list);
        const branches = list[0]
        // console.log('------------------> branches ', branches);

        return {
            availableBranches,
            branches,
            get allowedBranchIds() {
                return allowedBranchIds.slice();
            },
            get currentBranch() {
                return availableBranches[allowedBranchIds[0]];
            },
            setBranches(mode, ...branchIds) {
                // compute next branch ids
                let nextBranchIds;
                if (mode === "toggle") {
                    nextBranchIds = symmetricalDifference(allowedBranchIds, branchIds);
                } else if (mode === "loginto") {
                    const branchId = branchIds[0];
                    if (allowedBranchIds.length === 1) {
                        // 1 enabled branch: stay in single branch mode
                        nextBranchIds = [branchId];
                    } else {
                        // multi branch mode
                        nextBranchIds = [
                            branchId,
                            ...allowedBranchIds.filter((id) => id !== branchId),
                        ];
                    }
                }
                nextBranchIds = nextBranchIds.length ? nextBranchIds : [branchIds[0]];

                // apply them
                router.pushState({ bids: nextBranchIds }, { lock: true });
                cookie.setCookie("bids", nextBranchIds);
                // console.log('------------------> nextBranchIds ', nextBranchIds);
                ajax.jsonRpc('/set_brnach', 'call', {
                    'BranchID':  nextBranchIds,
                })
                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
            },
        };
    },
};

registry.category("services").add("branch", branchService);
