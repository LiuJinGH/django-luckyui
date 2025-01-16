function switch_list_card_check_all(i_ele) {
    // 全选控制
    console.log('switch_list_card_check_all:', i_ele)
    let $checkboxes = $('#list-card input.action-select');
    // 根据全选复选框的状态设置数据行复选框的状态
    $checkboxes.prop('checked', i_ele.checked);
}

function switch_card_check() {
    // 判断子选项是否都全选了
    console.log('switch_card_check:')
    let $checkboxes = $('#list-card input.action-select');
    let all_checked = $checkboxes.length === $checkboxes.filter(':checked').length;
    if (all_checked) {
        console.log('所有复选框都被选中了');
        $('#list-card #action-toggle').prop('checked', true);
    } else {
        console.log('有复选框都没被选中');
        $('#list-card #action-toggle').prop('checked', false);
    }
}
